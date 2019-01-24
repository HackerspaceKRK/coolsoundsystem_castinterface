# Cool Soundsystem - Castinterface

Pythonowy demon do przesyłania informacji z i do hakerspejsowych urządzeń typu __Google Chromecast__.

## Obecne funkcje:
- Przesyłanie na serwer MQTT w temacie `nazwa_urzadzenia/chromecast/status` statusu urządzenia
  - przykładowy dump:
```
        {
        	"data": {
        		"is_active_input": null,
        		"is_stand_by": null,
        		"volume_level": 1,
        		"volume_muted": false,
        		"app_id": "85CDB22F",
        		"display_name": "Chrome Audio Mirroring",
        		"namespaces": [
        			"urn:x-cast:com.google.cast.webrtc",
        			"urn:x-cast:com.google.cast.media",
        			"urn:x-cast:com.google.cast.debug",
        			"urn:x-cast:com.google.cast.remoting"
        		],
        		"session_id": "d2d6e001-93f0-4228-942e-7000549e327f",
        		"transport_id": "d2d6e001-93f0-4228-942e-7000549e327f",
        		"status_text": "www.youtube.com (Tab)"
        	},
        	"online": true
        }
```
- Przesyłanie na serwer MQTT w temacie `nazwa_urzadzenia/chromecast/playing` informacji o aktualnie granym utworze (w miarę możliwości - niektóre aplikacje dają bardzo mało danych)
  - przykładowy dump:
```
      {
    	"data": {
    		"current_time": 0,
    		"media_metadata": {
    			"metadataType": 0,
    			"title": ""
    		},
    		"subtitle_tracks": {},
    		"playback_rate": 1,
    		"media_custom_data": {},
    		"idle_reason": null,
    		"stream_type": "LIVE",
    		"player_state": "PLAYING",
    		"volume_level": 1,
    		"media_session_id": 0,
    		"content_type": "video/webm",
    		"duration": null,
    		"content_id": "",
    		"supported_media_commands": 0,
    		"current_subtitle_tracks": [],
    		"volume_muted": false
    	},
    	"online": true
    }
```
- Wymianę informacji - ciągłe wysyłanie i nasłuchiwanie zmian w stanie w temacie `nazwa_urzadzenia/chromecast/volume` i w razie zmiany - ustawianie głośności urządzenia (_pozwala to na np. embedowanie suwaka zmiany głośności na stronie internetowej_)
- Reagowanie na instrukcje `pause` i `play` na `nazwa_urzadzenia/chromecast/pause`
