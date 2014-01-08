/* -*-mode:c++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */

#include "cell_queue.hh"
#include "timestamp.hh"

using namespace std;

void CellQueue::read_packet( const string & contents )
{
    packet_queue_.emplace( timestamp() + delay_ms_, contents );
}

void CellQueue::write_packets( FileDescriptor & fd )
{
    while ( (!packet_queue_.empty())
            && (packet_queue_.front().first <= timestamp()) ) {
        fd.write( packet_queue_.front().second );
        packet_queue_.pop();
    }
}

int CellQueue::wait_time( void ) const
{
    return packet_queue_.empty() ? UINT16_MAX : (packet_queue_.front().first - timestamp());
}
