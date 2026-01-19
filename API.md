# 📡 API Documentation

Complete API reference for the Clap Detection application.

## Base URL

```
http://localhost:5000
```

## REST API Endpoints

### 1. Get Application Status

**Endpoint:** `GET /api/status`

**Description:** Get current application status

**Response:**
```json
{
  "is_listening": true,
  "yandex_connected": true,
  "audio_level": 0.05
}
```

**Fields:**
- `is_listening` (boolean): Whether audio detection is active
- `yandex_connected` (boolean): Whether Yandex API is initialized
- `audio_level` (number): Current audio input level (0.0 - 1.0)

---

### 2. Get Yandex Devices

**Endpoint:** `GET /api/devices`

**Description:** Retrieve list of configured Yandex smart devices

**Response:**
```json
{
  "devices": [
    {
      "id": "19a27edd-f48b-43d5-9a53-5d913cd9272b",
      "name": "Living Room Lamp",
      "type": "devices.types.light",
      "room": "Living Room",
      "capabilities": [...],
      "properties": [...]
    }
  ]
}
```

**Error Response:**
```json
{
  "error": "Yandex API not initialized"
}
```

---

### 3. Get Audio Input Devices

**Endpoint:** `GET /api/audio-devices`

**Description:** Get list of available audio input devices

**Response:**
```json
{
  "devices": [
    {
      "index": 0,
      "name": "Built-in Microphone",
      "channels": 2,
      "sample_rate": 44100
    },
    {
      "index": 1,
      "name": "USB Microphone",
      "channels": 1,
      "sample_rate": 48000
    }
  ]
}
```

---

### 4. Toggle Device

**Endpoint:** `POST /api/toggle`

**Description:** Manually toggle a specific device on/off

**Request Body:**
```json
{
  "device_id": "19a27edd-f48b-43d5-9a53-5d913cd9272b"
}
```

**Response:**
```json
{
  "success": true
}
```

**Error Response:**
```json
{
  "error": "device_id required"
}
```

---

### 5. Start Calibration

**Endpoint:** `POST /api/calibrate`

**Description:** Run audio calibration to determine optimal threshold

**Request Body (Optional):**
```json
{
  "duration": 3.0
}
```

**Response:**
```json
{
  "min": 0.001,
  "max": 0.456,
  "mean": 0.123,
  "std": 0.089,
  "suggested_threshold": 0.234
}
```

**Fields:**
- `min` (number): Minimum audio level detected
- `max` (number): Maximum audio level detected
- `mean` (number): Average audio level
- `std` (number): Standard deviation
- `suggested_threshold` (number): Recommended threshold value

---

### 6. Get Settings

**Endpoint:** `GET /api/settings`

**Description:** Retrieve current application settings

**Response:**
```json
{
  "audio": {
    "sample_rate": 44100,
    "chunk_size": 2048,
    "threshold": 50,
    "min_clap_interval": 100,
    "max_clap_interval": 500,
    "clap_min_freq": 2000,
    "clap_max_freq": 4000,
    "debounce_time": 1000,
    "selected_device": 0
  },
  "yandex_devices": [
    "19a27edd-f48b-43d5-9a53-5d913cd9272b",
    "72a33ab1-6a1d-4b98-a811-8a98bfeb873d",
    "95cf0e1e-8117-4248-a87a-f7d83a1c50b1"
  ]
}
```

---

### 7. Update Settings

**Endpoint:** `POST /api/settings`

**Description:** Update application settings

**Request Body:**
```json
{
  "audio": {
    "threshold": 60,
    "min_clap_interval": 150,
    "max_clap_interval": 450,
    "selected_device": 1
  }
}
```

**Response:**
```json
{
  "success": true
}
```

---

### 8. Get Event History

**Endpoint:** `GET /api/events`

**Description:** Retrieve event log

**Response:**
```json
{
  "events": [
    {
      "type": "double_clap",
      "message": "Double clap detected",
      "timestamp": "2024-01-19T12:34:56.789Z"
    },
    {
      "type": "toggle_devices",
      "message": "Toggled 3/3 devices",
      "timestamp": "2024-01-19T12:34:57.123Z"
    }
  ]
}
```

**Event Types:**
- `double_clap` - Double clap detected
- `toggle_devices` - Devices toggled
- `manual_toggle` - Manual device toggle
- `calibration_start` - Calibration started
- `calibration_complete` - Calibration completed
- `listening_start` - Audio detection started
- `listening_stop` - Audio detection stopped
- `settings_update` - Settings updated
- `error` - Error occurred

---

### 9. Control Listening State

**Endpoint:** `POST /api/listening`

**Description:** Start or stop audio detection

**Request Body:**
```json
{
  "listening": true
}
```

**Response:**
```json
{
  "listening": true
}
```

---

## WebSocket Events

Connect to WebSocket at `ws://localhost:5000`

### Client → Server Events

#### 1. start_listening

**Description:** Request to start audio detection

**Payload:** None

---

#### 2. stop_listening

**Description:** Request to stop audio detection

**Payload:** None

---

### Server → Client Events

#### 1. connect

**Description:** Client connected to server

**Payload:** None

---

#### 2. status

**Description:** Application status update

**Payload:**
```json
{
  "is_listening": true,
  "yandex_connected": true
}
```

---

#### 3. audio_level

**Description:** Real-time audio level update (sent continuously while listening)

**Payload:**
```json
{
  "level": 0.123
}
```

**Frequency:** ~20-50 times per second

---

#### 4. clap_detected

**Description:** Single clap detected

**Payload:**
```json
{
  "timestamp": 1705668896.789,
  "level": 0.456
}
```

---

#### 5. device_toggled

**Description:** Devices were toggled

**Payload:**
```json
{
  "timestamp": "2024-01-19T12:34:56.789Z",
  "results": {
    "19a27edd-f48b-43d5-9a53-5d913cd9272b": true,
    "72a33ab1-6a1d-4b98-a811-8a98bfeb873d": true,
    "95cf0e1e-8117-4248-a87a-f7d83a1c50b1": false
  }
}
```

---

#### 6. event

**Description:** General event notification

**Payload:**
```json
{
  "type": "double_clap",
  "message": "Double clap detected",
  "timestamp": "2024-01-19T12:34:56.789Z"
}
```

---

## Error Codes

### HTTP Status Codes

- `200 OK` - Success
- `400 Bad Request` - Invalid request parameters
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "error": "Error message description"
}
```

---

## Rate Limiting

No rate limiting is currently implemented. Use responsibly.

---

## Authentication

No authentication required for local use. For production deployment, implement proper authentication.

---

## CORS

CORS is enabled for all origins (`*`). Restrict in production.

---

## Examples

### JavaScript/Fetch

```javascript
// Get status
fetch('http://localhost:5000/api/status')
  .then(res => res.json())
  .then(data => console.log(data));

// Toggle device
fetch('http://localhost:5000/api/toggle', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    device_id: '19a27edd-f48b-43d5-9a53-5d913cd9272b' 
  })
})
  .then(res => res.json())
  .then(data => console.log(data));

// Update settings
fetch('http://localhost:5000/api/settings', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    audio: { threshold: 60 } 
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### Python/Requests

```python
import requests

# Get status
response = requests.get('http://localhost:5000/api/status')
print(response.json())

# Toggle device
response = requests.post(
    'http://localhost:5000/api/toggle',
    json={'device_id': '19a27edd-f48b-43d5-9a53-5d913cd9272b'}
)
print(response.json())

# Update settings
response = requests.post(
    'http://localhost:5000/api/settings',
    json={'audio': {'threshold': 60}}
)
print(response.json())
```

### cURL

```bash
# Get status
curl http://localhost:5000/api/status

# Toggle device
curl -X POST http://localhost:5000/api/toggle \
  -H "Content-Type: application/json" \
  -d '{"device_id": "19a27edd-f48b-43d5-9a53-5d913cd9272b"}'

# Update settings
curl -X POST http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"audio": {"threshold": 60}}'

# Start calibration
curl -X POST http://localhost:5000/api/calibrate \
  -H "Content-Type: application/json" \
  -d '{"duration": 3.0}'
```

### WebSocket (JavaScript)

```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Listen for events
socket.on('connect', () => {
  console.log('Connected to server');
});

socket.on('audio_level', (data) => {
  console.log('Audio level:', data.level);
});

socket.on('clap_detected', (data) => {
  console.log('Clap detected at', data.timestamp);
});

socket.on('device_toggled', (data) => {
  console.log('Devices toggled:', data.results);
});

socket.on('event', (data) => {
  console.log('Event:', data.type, data.message);
});

// Send events
socket.emit('start_listening');
socket.emit('stop_listening');
```

---

## Data Models

### Device Object

```typescript
interface Device {
  id: string;              // Unique device ID
  name: string;            // Device name
  type: string;            // Device type (e.g., "devices.types.light")
  room: string;            // Room name
  capabilities: array;     // Device capabilities
  properties: array;       // Device properties
}
```

### AudioDevice Object

```typescript
interface AudioDevice {
  index: number;           // Device index
  name: string;            // Device name
  channels: number;        // Number of input channels
  sample_rate: number;     // Default sample rate in Hz
}
```

### Event Object

```typescript
interface Event {
  type: string;            // Event type
  message: string;         // Event message
  timestamp: string;       // ISO 8601 timestamp
}
```

---

## Best Practices

1. **Check status** before making requests
2. **Handle errors** gracefully
3. **Use WebSocket** for real-time updates
4. **Cache device list** to reduce API calls
5. **Debounce** frequent operations
6. **Validate input** before sending

---

## Changelog

### v1.0.0
- Initial API release
- All core endpoints implemented
- WebSocket support added

---

**For more information, see the main [README.md](README.md)**
