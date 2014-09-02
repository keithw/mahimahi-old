/* -*-mode:c++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */

#include <limits>
#include <cassert>
#include <thread>

#include "meter_queue.hh"
#include "util.hh"
#include "timestamp.hh"

using namespace std;

MeterQueue::MeterQueue( const string & name, const bool graph )
    : packet_queue_(),
      graph_( nullptr ),
      bytes_this_bin_( 0 ),
      bin_width_( 250 ),
      current_bin_( timestamp() / bin_width_ ),
      logical_width_( graph ? max( 5.0, 640 / 100.0 ) : 1 )
{
    assert_not_root();

    if ( graph ) {
        graph_.reset( new Graph( 1, 640, 480, name, 0, 1 ) );
        graph_->set_color( 0, 1, 0, 0, 0.5 );
        thread newthread( [&] () {
                while ( true ) {
                    graph_->blocking_draw( timestamp() / 1000.0, logical_width_, 0, 10 );
                }
            } );
        newthread.detach();
    }
}

void MeterQueue::advance( void )
{
    assert( graph_ );

    const uint64_t now_bin = timestamp() / bin_width_;

    if ( current_bin_ == now_bin ) {
        return;
    }

    while ( current_bin_ < now_bin ) {
        graph_->add_data_point( 0,
                                current_bin_ * bin_width_ / 1000.0,
                                (bytes_this_bin_ * 8.0 / (bin_width_ / 1000.0)) / 1000000.0 );
        bytes_this_bin_ = 0;
        current_bin_++;
    }

    /* cull the data */
    logical_width_ = max( 5.0, graph_->size().first / 100.0 );
    graph_->set_window( current_bin_ * bin_width_ / 1000.0, logical_width_ );
}

void MeterQueue::read_packet( const string & contents )
{
    packet_queue_.emplace( contents );

    /* save it */
    if ( graph_ ) {
        advance();
        bytes_this_bin_ += contents.size();
    }
}

void MeterQueue::write_packets( FileDescriptor & fd )
{
    while ( not packet_queue_.empty() ) {
        fd.write( packet_queue_.front() );
        packet_queue_.pop();
    }
}

unsigned int MeterQueue::wait_time( void ) const
{
    return packet_queue_.empty() ? numeric_limits<uint16_t>::max() : 0;
}
