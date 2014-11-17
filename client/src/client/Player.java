package client;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import com.firebase.client.*;


public class Player {
	// We listen to all of these variables and on every change we update the entry
	// We will have an instance of the player class for the two players
	
	// Who will update the moves? We may still update them and leave the listener
	// The other player's moves should be entirely to the listener, while ours 
	// will be update by both server and client
	Firebase player_node;
	List<Card> hand, discard, constructs;
	List<Move> moves;
	Long honor;
	
	public Player(Firebase player_node) throws Exception {
		this.player_node = player_node;
		
		// how to java?
		addListener(player_node.child("moves"), 0);
		addListener(player_node.child("hand"), 1);
		addListener(player_node.child("discard"), 2);
		addListener(player_node.child("constructs"), 3);
		addListener(player_node.child("honor"), 4);
	}
	
	protected List<Move> getListofMovesFromSnapshot(DataSnapshot snapshot) {
		return null;
		//Parse moves
	}

	protected List<Card> getListofCardsFromSnapshot(DataSnapshot snapshot) {
		Map<String, Object> cards = (Map<String, Object>)snapshot.getValue();
		List<Card> parsedList = new LinkedList<Card>();
		
		if (cards == null) {
			return parsedList;
		}
		
		for (Map.Entry<String, Object> entry : cards.entrySet()) {
			Card key = new Card(entry.getKey());
			Long times = (Long) entry.getValue();
			
			while (times != 0) {
				parsedList.add(key);
				-- times;
			}
		}
		System.out.println(parsedList);
		return parsedList;
	}
	
	private void addListener(Firebase child, final int fml) {
		child.addValueEventListener(new ValueEventListener() {
		    @Override
		    public void onDataChange(DataSnapshot snapshot) {
		    	switch(fml) {
		    	case 0:
		    		moves = getListofMovesFromSnapshot(snapshot);
		    		break;
		    	case 1:
		    		hand = getListofCardsFromSnapshot(snapshot);
		    		break;
		    	case 2:
		    		discard = getListofCardsFromSnapshot(snapshot);
		    		break;
		    	case 3:
		    		constructs = getListofCardsFromSnapshot(snapshot);
		    		break;
		    	case 4:
		    		honor = (Long) snapshot.getValue();
		    		break;
		    	default:
		    		assert(false);
		    	}
		    }
		    @Override
		    public void onCancelled(FirebaseError firebaseError) {
		    	assert(false);
		    }
		});
	}
}
