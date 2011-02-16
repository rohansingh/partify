package com.rohanradio.partify;

public class Track {
	private String artistName;
	
	private String title;
	
	public Track(String artistName, String trackName) {
		this.artistName = artistName;
		this.title = trackName;
	}

	public String getArtistName() {
		return this.artistName;
	}

	public String getTitle() {
		return this.title;
	}
}
