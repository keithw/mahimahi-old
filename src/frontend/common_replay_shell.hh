/* -*-mode:c++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */

#ifndef COMMONREPLAYSHELL_HH
#define COMMONREPLAYSHELL_HH

#include <string>

#include <net/route.h>
#include <fcntl.h>

#include <vector>
#include <set>

#include "util.hh"
#include "netdevice.hh"
#include "web_server.hh"
#include "system_runner.hh"
#include "socket.hh"
#include "event_loop.hh"
#include "temp_file.hh"
#include "http_response.hh"
#include "dns_server.hh"
#include "exception.hh"

#include "http_record.pb.h"

#include "config.h"

using namespace std;

class CommonReplayShell
{

private: 
    void add_dummy_interface( const string & name, const Address & addr );
    bool isYoutubeServer; 

public:
    CommonReplayShell( bool isYoutubeServer );
    int run_replay_shell(int argc, char *argv[]);
};

#endif
