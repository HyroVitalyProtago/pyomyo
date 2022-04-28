class pyomyo {
  static Mode = {
    NO_DATA: 0, // Do not send EMG data
    PREPROCESSED: 1, // Sends 50Hz rectified and band pass filtered data
    FILTERED: 2, // Sends 200Hz filtered but not rectified data
    RAW: 3, // Sends raw 200Hz data from the ADC ranged between -128 and 127
  };

  static Arm = {
    UNKNOWN: 0,
    RIGHT: 1,
    LEFT: 2,
  };

  static XDirection = {
    UNKNOWN: 0,
    X_TOWARD_WRIST: 1,
    X_TOWARD_ELBOW: 2,
  };

  static Pose = {
    REST: 0,
    FIST: 1,
    WAVE_IN: 2,
    WAVE_OUT: 3,
    FINGERS_SPREAD: 4,
    THUMB_TO_PINKY: 5,
    UNKNOWN: 255,
  };

  constructor(host, port) {
    const self = this;
    self.sock = new WebSocket("ws://" + host + ":" + port);
    self.sock.onmessage = (message) => self.onmessage(message);
    self.sock.onopen = (e) => self.onopen(e);
    self.sock.onclose = (e) => self.onclose(e);
  }

  onopen(e) {
    console.log("Connected !");
  }
  onclose(e) {
    console.log("Socket is closed.", e.reason);
  }

  onmessage(msg) {
    //console.log(msg)
    const json = JSON.parse(msg.data);
    switch (json.type) {
      case "connect":
        console.log(json.message);
        break;
      case "emg":
        this.onemg(json.data);
        break;
      case "imu":
        this.onimu(json.data);
        break;
      case "pose":
        this.onpose(json.data);
        break;
      case "arm":
        this.onarm(json.data);
        break;
      case "battery":
        this.onbattery(json.data);
        break;
      default:
        throw "Unexpected message type: " + json.type;
    }
  }
  send(message) {
    if (this.sock && this.sock.readyState === WebSocket.OPEN)
      this.sock.send(JSON.stringify(message));
  }
  onclose(e) {
    if (this.sock) this.sock.close();
  }

  connect(mode) {
    console.log("try to connect in mode " + mode);
    this.send({
      type: "connect",
      mode: mode,
    });
  }

  vibrate(value) {
    this.send({
      type: "vibrate",
      value: value,
    });
  }

  setLEDs(logoColor, lineColor) {
    this.send({
      type: "set_leds",
      logo: logoColor,
      line: lineColor,
    });
  }

  // {"type": "emg", "data": [70, 136, 438, 155, 43, 51, 125, 94]}
  onemg(emgs) {}
  // {"type": "imu", "data": [-8658, 2485, -1778, 13569]}
  onimu(data) {}
  onpose(data) {}
  onarm(data) {}
  onbattery(data) {}
}
