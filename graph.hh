#ifndef GRAPH_HH
#define GRAPH_HH

#include <deque>
#include <vector>
#include <mutex>

#include "display.hh"
#include "cairo_objects.hh"

class Graph
{
  struct GraphicContext
  {
    XPixmap pixmap;
    Cairo cairo;
    Pango pango;

    GraphicContext( XWindow & window );
  };

  XWindow window_;
  std::array<GraphicContext, 3> gcs_;
  unsigned int current_gc_;

  GraphicContext & current_gc( void );

  Pango::Font tick_font_;
  Pango::Font label_font_;

  struct YLabel
  {
    int height;
    Pango::Text text;
    float intensity;
  };

  std::deque<std::pair<int, Pango::Text>> x_tick_labels_;
  std::vector<YLabel> y_tick_labels_;
  std::vector<std::tuple<float, float, float, float>> colors_;
  std::vector<std::deque<std::pair<float, float>>> data_points_;

  Pango::Text x_label_;
  Pango::Text y_label_;

  std::string info_string_;
  Pango::Text info_;

  float bottom_, top_;

  float project_height( const float x ) const { return ( x - bottom_ ) / ( top_ - bottom_ ); }
  float chart_height( const float x, const unsigned int window_height ) const
  {
    return (window_height - 40) * (.825*(1-project_height( x ))+.025) + (.825 * 40);
  }

  Cairo::Pattern horizontal_fadeout_;

  std::mutex data_mutex_;

public:
  Graph( const unsigned int num_lines,
	 const unsigned int initial_width, const unsigned int initial_height, const std::string & title,
	 const float min_y, const float max_y );

  void set_window( const float t, const float logical_width );
  void add_data_point( const unsigned int num, const float t, const float y ) {
    std::unique_lock<std::mutex> ul { data_mutex_ };

    if ( not data_points_.at( num ).empty() ) {
      if ( y == data_points_.at( num ).back().second ) {
	return;
      }
    }

    data_points_.at( num ).emplace_back( t, y );
  }

  void set_color( const unsigned int num, const float red, const float green, const float blue,
		  const float alpha );

  bool blocking_draw( const float t, const float logical_width, const float min_y, const float max_y );

  void set_info( const std::string & info );

  std::pair<unsigned int, unsigned int> size( void ) const { return window_.size(); }
};

#endif /* GRAPH_HH */
