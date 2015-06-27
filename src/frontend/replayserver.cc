/* -*-mode:c++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#include <iostream>
#include <vector>
#include <limits>
#include <sstream>
#include <fstream>

#include "util.hh"
#include "http_record.pb.h"
#include "http_header.hh"
#include "exception.hh"
#include "http_request.hh"
#include "http_response.hh"
#include "file_descriptor.hh"
#include "ezio.hh"

using namespace std;

string safe_getenv( const string & key )
{
    const char * const value = getenv( key.c_str() );
    if ( not value ) {
        throw runtime_error( "missing environment variable: " + key );
    }
    return value;
}

/* does the actual HTTP header match this stored request? */
bool header_match( const string & env_var_name,
                   const string & header_name,
                   const HTTPRequest & saved_request )
{
    const char * const env_value = getenv( env_var_name.c_str() );

    /* case 1: neither header exists (OK) */
    if ( (not env_value) and (not saved_request.has_header( header_name )) ) {
        return true;
    }

    /* case 2: headers both exist (OK if values match) */
    if ( env_value and saved_request.has_header( header_name ) ) {
        return saved_request.get_header_value( header_name ) == string( env_value );
    }

    /* case 3: one exists but the other doesn't (failure) */
    return false;
}

string strip_query( const string & request_line )
{
    const auto index = request_line.find( "?" );
    if ( index == string::npos ) {
        return request_line;
    } else {
        return request_line.substr( 0, index );
    }
}

/* compare request_line and certain headers of incoming request and stored request */
unsigned int match_score( const MahimahiProtobufs::RequestResponse & saved_record,
                          const string & request_line,
                          const bool is_https )
{
    const HTTPRequest saved_request( saved_record.request() );

    /* match HTTP/HTTPS */
    if ( is_https and (saved_record.scheme() != MahimahiProtobufs::RequestResponse_Scheme_HTTPS) ) {
        return 0;
    }

    if ( (not is_https) and (saved_record.scheme() != MahimahiProtobufs::RequestResponse_Scheme_HTTP) ) {
        return 0;
    }

    /* match host header */
    if ( not header_match( "HTTP_HOST", "Host", saved_request ) ) {
        return 0;
    }

    /* match user agent */
    if ( not header_match( "HTTP_USER_AGENT", "User-Agent", saved_request ) ) {
        return 0;
    }

    /* must match first line up to "?" at least */
    if ( strip_query( request_line ) != strip_query( saved_request.first_line() ) ) {
        return 0;
    }

    /* success! return size of common prefix */
    const auto max_match = min( request_line.size(), saved_request.first_line().size() );
    for ( unsigned int i = 0; i < max_match; i++ ) {
        if ( request_line.at( i ) != saved_request.first_line().at( i ) ) {
            return i;
        }
    }

    return max_match;
}


bool is_youtube_media_request( const string & first_line ) {
    return first_line.find( "GET /videoplayback?" ) == 0;
}

//This will return the string representation of a parameter value within the uri. 
//For example to get the 'clen' parameter, you can call get_param("clen", request_line)
string get_param(string parameter_name, string uri) {
    string formatted_parameter = "&" + parameter_name + "=";
    size_t start_position = uri.find( formatted_parameter );
    if( start_position == string::npos ) {
        throw runtime_error( "no valid " + parameter_name + " parameter found in the YouTube video-playback request uri" );
    }
    size_t formatted_parameter_length = formatted_parameter.length();
    string parameter_value_string = uri.substr( start_position + formatted_parameter_length, uri.find( '&', start_position + formatted_parameter_length ) - (start_position + formatted_parameter_length) );
    return parameter_value_string;
}


int main( void )
{
    try {
        assert_not_root();

        const string working_directory = safe_getenv( "MAHIMAHI_CHDIR" );
        const string recording_directory = safe_getenv( "MAHIMAHI_RECORD_PATH" );
        const string request_line = safe_getenv( "REQUEST_METHOD" )
            + " " + safe_getenv( "REQUEST_URI" )
            + " " + safe_getenv( "SERVER_PROTOCOL" );
        const bool is_https = getenv( "HTTPS" );

        SystemCall( "chdir", chdir( working_directory.c_str() ) );

        const vector< string > files = list_directory_contents( recording_directory );

        unsigned int best_score = 0;
        MahimahiProtobufs::RequestResponse best_match;

        for ( const auto & filename : files ) {
            FileDescriptor fd( SystemCall( "open", open( filename.c_str(), O_RDONLY ) ) );
            MahimahiProtobufs::RequestResponse current_record;
            if ( not current_record.ParseFromFileDescriptor( fd.fd_num() ) ) {
                throw runtime_error( filename + ": invalid HTTP request/response" );
            }

            unsigned int score = match_score( current_record, request_line, is_https );
            if ( score > best_score ) {
                best_match = current_record;
                best_score = score;
            }
        }

        //The request line contains the command and uri. Youtube media requests for audio and video contain GET /videoplayback? in the request line. 
        if(is_youtube_media_request(request_line) && best_score > 0) {
            /* Log the request meta data to the logfile */
            FileDescriptor logfile( SystemCall( "open", open("./tmp/the_shot_trey_burke_logfile.txt", O_WRONLY | O_APPEND | O_CREAT, S_IRUSR | S_IWUSR)));
            const string scheme = is_https? "https" : "http";
            const string host = safe_getenv("HTTP_HOST");
            
            size_t range_start = request_line.find( "&range=" );
            size_t range_mid   = request_line.find( '-', range_start );
            size_t range_end   = request_line.find( '&', range_mid );
            if( range_start == string::npos || range_mid == string::npos ) {
                throw runtime_error( "no valid range parameter found in the YouTube video-playback request uri" );
            }

            off_t chunk_offset = atoll( request_line.substr( range_start + 7, range_mid - (range_start + 7) ).c_str() );
            off_t chunk_last   = atoll( request_line.substr( range_mid   + 1, range_end - (range_mid   + 1) ).c_str() );
            off_t chunk_len = chunk_last - chunk_offset + 1;


            // For YouTube media requests the requested media file size is expressed as a uri parameter. 
            // For example: &clen=153400, which means that we should look for a byte range in a file of size 153400. 
            string clen_str = get_param("clen", request_line);
            off_t clen = atoll( clen_str.c_str() );


            // For YouTube media requests the MIME format (audio or video) is expressed as a uri parameter. 
            // For example: &mime=video%2Fwebm, which means that we have a webm video request
            string mime_str = get_param("mime", request_line);

            size_t slash_position = mime_str.find("%2F");
            mime_str.replace(slash_position, string("%2F").length(), "/");

            string requested_file_directory = working_directory + "/media_files/the_shot_trey_burke_media_files/" + mime_str + "/";
            vector<string> filenames; 
            string requested_filename = "";
            filenames = list_directory_contents( requested_file_directory );
            for( auto & filename : filenames ) {
                struct stat fileinfo; 
                SystemCall( "stat", stat( filename.c_str(), &fileinfo ));
                if(clen == fileinfo.st_size) {
                    requested_filename = filename;
                    break;
                }
            }

            if( requested_filename == "" ) {
                throw runtime_error( "could not find a file with format " + mime_str + " and size " + clen_str + " on the YouTube server");
            }
          

            HTTPResponse response = HTTPResponse(); 
        

            HTTPRequest request = HTTPRequest();
            request.set_first_line( request_line );
           
            response.set_request(request);

            HTTPResponse best_match_response = HTTPResponse(best_match.response()); 

            
           
            response.set_first_line( best_match_response.first_line() ); //Set the first line of response to the actual request line

            /* Set the headers of the response to the headers of the best match for the request 
               i.e. only the body and request are different from the best match */
             

            std::vector< HTTPHeader > best_match_response_headers = best_match_response.get_headers(); 
            for( const auto & header : best_match_response_headers) {
                 response.add_or_replace_header(header);
            }
         

            response.add_or_replace_header( HTTPHeader("Content-Length:" + to_string(chunk_len)));
            response.add_or_replace_header( HTTPHeader("Content-Type:" + mime_str));
           
            response.done_with_headers(); 
        
             
            ifstream file{ requested_filename, ifstream::in | ifstream::binary };
            file.seekg( chunk_offset, ifstream::beg );

            char * buf = new char[chunk_len];
            file.read( buf, chunk_len );

            stringstream body_stream; 
            body_stream.write(buf, chunk_len);
           
            response.read_in_body( body_stream.str() ); //Set the content of the response to the data chunk from the media file

            delete[] buf;

            cout << response.str();


            return EXIT_SUCCESS;
        } else if ( best_score > 0 ) { /* give client the best match */
            cout << HTTPResponse( best_match.response() ).str();
            return EXIT_SUCCESS;
        } else {                /* no acceptable matches for request */
            cout << "HTTP/1.1 404 Not Found" << CRLF;
            cout << "Content-Type: text/plain" << CRLF << CRLF;
            cout << "replayserver: could not find a match for " << request_line << CRLF;
            return EXIT_FAILURE;
        }
    } catch ( const exception & e ) {
        cout << "HTTP/1.1 500 Internal Server Error" << CRLF;
        cout << "Content-Type: text/plain" << CRLF << CRLF;
        cout << "mahimahi mm-webreplay received an exception:" << CRLF << CRLF;
        print_exception( e, cout );
        return EXIT_FAILURE;
    }
}
