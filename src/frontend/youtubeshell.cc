/* -*-mode:c++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */

#include "common_replay_shell.hh"

int main( int argc, char *argv[] )
{
    CommonReplayShell replay_runner = CommonReplayShell(true);
    return replay_runner.run_replay_shell(argc, argv);
}
