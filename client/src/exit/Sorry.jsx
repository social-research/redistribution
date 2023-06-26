import { usePlayer } from "@empirica/core/player/classic/react";
import React from "react";
import { Button } from "../components/Button";

export function Sorry() {

  const player = usePlayer();

  let msg;
  // This all was copied from guess-the-correlation
  // TO DO!!! - check in the guess-the-correlation folder where exitStatus is specified and do same here
  // Update code below to show correct message
  switch (player.exitStatus) {
    case "gameFull":
      msg = "All games you are eligible for have filled up too fast...";
      break;
    case "gameLobbyTimedOut":
      msg = "There were NOT enough players for the game to start..";
      break;
    // case "playerLobbyTimedOut":
    //   msg = "???";
    //   break;
    case "playerEndedLobbyWait":
      msg =
        "You decided to stop waiting, we are sorry it was too long a wait.";
      break;
    default:
      msg = "Unfortunately the Game was cancelled...";
      break;


    return (
      <Centered>
        <div className="score">
          <h1>Sorry!</h1>

          <p>Sorry, you were not able to play today! {msg}</p>

          {/*{player.exitStatus !== "gameFull" ? (*/}

          {/*<p>*/}
          {/*Please return the HIT now so our platform does register your MTurk.*/}
          {/*Please come back for one of the next batches. We will submit new*/}
          {/*batches on Monday the 6th of August and Tuesday the 7th of August*/}
          {/*(batches of 100 games every hour starting at 2PM ET until 5PM).*/}
          {/*</p>*/}

          {player.exitStatus === "gameLobbyTimedOut" ? (
            <p>
              Please submit <em>{player.id}</em> as the payment code in order to
              receive the $1 base payment for your time today. 
            </p>
          ) : null}

          {player.exitStatus === "gameFull" ? (
            <p>
              Please submit <em>FZgameFullCSOP213093</em> as the survey code in
              order to receive the $0.1 showing up bonus.
            </p>
          ) : null}

          {/*) : (*/}
          {/*<p>*/}
          {/*Please click on: <strong>Reset current session</strong> from the*/}
          {/*top right side of the page (if it appears for you) to see if there*/}
          {/*are other games that you could join now. Note you will need to go*/}
          {/*over the instructions and quiz again (they might be different for*/}
          {/*different games). Otherwise, Please return the HIT now so our*/}
          {/*platform does not register your MTurk ID as someone who already*/}
          {/*participated.*/}
          {/*</p>*/}

          <p>
            <strong>Please come back for the next scheduled game.</strong>{" "}
            {/*We will send an email notification once the next  HIT is scheduled.*/}
          </p>

          {/*This is not really needed .. all of these people failed to start the game .. if we allow them to submit, then their data will be deleted, we don't want that*/}
          <p>
            {/*{hasNext ? (*/}
              {/*<Button*/}
                {/*intent={"primary"}*/}
                {/*type="button"*/}
                {/*onClick={() => onSubmit()}*/}
              {/*>*/}
                {/*Done*/}
              {/*</Button>*/}
            {/*) : (*/}
              {/*""*/}
            {/*)}*/}
          </p>
        </div>
      </Centered>
    );
  }
}