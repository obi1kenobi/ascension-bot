package client;
import java.util.HashMap;

import com.firebase.client.*;


public class Main {
	static String FIREBASE_URL = "https://ascension-bot.firebaseio.com";
	static String game_id = "-Jaw97SDeYJksJ8maXbN";
	public static void main(String args[]) throws Exception {
		Firebase firebase = new Firebase(FIREBASE_URL);
		Firebase game = firebase.child("/games/" + game_id + "/players/");
		
		// Insert the player into the tree
		Firebase player_node = game.push();
		player_node.setValue("");
		
		// Now we need to block and wait for the server to
		// tell us that it is our turn, then fetch information about
		// the board, about the current player, about the other players
		
	
		System.out.println("Sleeping while initialize honor");
		Thread.sleep(5000);
		Player p = new Player(player_node);
		
		while (true) {
			System.out.println(p.honor);
			Thread.sleep(1000);
		}
	}
}
