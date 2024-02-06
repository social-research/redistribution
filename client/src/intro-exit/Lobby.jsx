import { usePlayer } from "@empirica/core/player/classic/react";
import React, { useState, useEffect } from "react";
import { P } from "../components/TextStyles";

export function Lobby() {
  const player = usePlayer();
  const [lobbyTimeout, setLobbyTimeout] = useState(false);

  useEffect(() => {
    console.log(`Lobby`);
    const timeout = 1 * 60 * 1000; // seconds, so 1 minute - UPDATE TO 5 MINUTES: 5 * 60 * 1000 !!!!
    setTimeout(() => setLobbyTimeout(true), timeout);
  }, []);

  const renderInitialMessage = () => (
    <>
      <h3 className="mt-2 mb-5 text-sm font-medium text-gray-900">Waiting...</h3>
      <P>
        We are waiting for other participants to join the study. When enough
        participants have joined, your study will start.
      </P>
      <P>This should take less than 5 minutes.</P>
    </>
  );

  const renderTimeoutMessage = () => (
    <>
      <h3 className="mt-2 text-sm font-medium text-gray-900">
        Unfortunately, it's taking longer than we expected to match you with a group.
      </h3>
      <p>
        You can choose to either wait a bit longer or leave the study.
      </p>
      <p>
        If you choose to leave, please submit the following code to be paid for your time: {player.id}408
      </p>
    </>
  );

  return (
    <div className="flex h-full items-center justify-center">
      <div className="text-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 640 512"
          className="mx-auto h-12 w-12 text-gray-400"
          stroke="none"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M544 224c44.2 0 80-35.8 80-80s-35.8-80-80-80-80 35.8-80 80 35.8 80 80 80zm0-128c26.5 0 48 21.5 48 48s-21.5 48-48 48-48-21.5-48-48 21.5-48 48-48zM320 256c61.9 0 112-50.1 112-112S381.9 32 320 32 208 82.1 208 144s50.1 112 112 112zm0-192c44.1 0 80 35.9 80 80s-35.9 80-80 80-80-35.9-80-80 35.9-80 80-80zm244 192h-40c-15.2 0-29.3 4.8-41.1 12.9 9.4 6.4 17.9 13.9 25.4 22.4 4.9-2.1 10.2-3.3 15.7-3.3h40c24.2 0 44 21.5 44 48 0 8.8 7.2 16 16 16s16-7.2 16-16c0-44.1-34.1-80-76-80zM96 224c44.2 0 80-35.8 80-80s-35.8-80-80-80-80 35.8-80 80 35.8 80 80 80zm0-128c26.5 0 48 21.5 48 48s-21.5 48-48 48-48-21.5-48-48 21.5-48 48-48zm304.1 180c-33.4 0-41.7 12-80.1 12-38.4 0-46.7-12-80.1-12-36.3 0-71.6 16.2-92.3 46.9-12.4 18.4-19.6 40.5-19.6 64.3V432c0 26.5 21.5 48 48 48h288c26.5 0 48-21.5 48-48v-44.8c0-23.8-7.2-45.9-19.6-64.3-20.7-30.7-56-46.9-92.3-46.9zM480 432c0 8.8-7.2 16-16 16H176c-8.8 0-16-7.2-16-16v-44.8c0-16.6 4.9-32.7 14.1-46.4 13.8-20.5 38.4-32.8 65.7-32.8 27.4 0 37.2 12 80.2 12s52.8-12 80.1-12c27.3 0 51.9 12.3 65.7 32.8 9.2 13.7 14.1 29.8 14.1 46.4V432zM157.1 268.9c-11.9-8.1-26-12.9-41.1-12.9H76c-41.9 0-76 35.9-76 80 0 8.8 7.2 16 16 16s16-7.2 16-16c0-26.5 19.8-48 44-48h40c5.5 0 10.8 1.2 15.7 3.3 7.5-8.5 16.1-16 25.4-22.4z" />
        </svg>
        {!lobbyTimeout && renderInitialMessage()}
        {lobbyTimeout && renderTimeoutMessage()}
      </div>
    </div>
  );
}