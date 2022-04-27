using System;
using System.Linq;
using UnityEngine;
using WebSocketSharp;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

// Based on https://github.com/PerlinWarp/pyomyo/blob/main/src/pyomyo/pyomyo.py
// Require Newtonsoft.Json and WebSocketSharp
public class Myo : MonoBehaviour {
    public enum Mode {
        NO_DATA = 0, // Do not send EMG data
        PREPROCESSED = 1, // Sends 50Hz rectified and band pass filtered data
        FILTERED = 2, // Sends 200Hz filtered but not rectified data
        RAW = 3, // Sends raw 200Hz data from the ADC ranged between -128 and 127
    }

    public enum Arm {
        UNKNOWN = 0,
        RIGHT = 1,
        LEFT = 2
    }

    public enum XDirection {
        UNKNOWN = 0,
        X_TOWARD_WRIST = 1,
        X_TOWARD_ELBOW = 2
    }

    public enum Pose {
        REST = 0,
        FIST = 1,
        WAVE_IN = 2,
        WAVE_OUT = 3,
        FINGERS_SPREAD = 4,
        THUMB_TO_PINKY = 5,
        UNKNOWN = 255
    }

    [SerializeField] string _ip = "localhost";
    [SerializeField] int _port = 9898;
    [SerializeField] bool _autoConnect;
    [SerializeField] Mode _mode;
    
    WebSocket _webSocket;
    
    void OnEnable() {
        _webSocket = new WebSocket(string.Format("ws://{0}:{1}", _ip, _port));
        _webSocket.OnMessage += OnMessage;
        _webSocket.Connect();
        if (_autoConnect) Connect(_mode);
    }

    void OnDisable() {
        _webSocket.Close();
    }

    void OnMessage(object sender, MessageEventArgs args) {
        var json = JObject.Parse(args.Data);
        switch (json["type"].ToString()) {
            case "connect":
                Debug.Log(json["message"]);
                break;
            case "emg":
                OnEMG(json["data"]);
                break;
            case "imu":
                OnIMU(json["data"]);
                break;
            case "pose":
                OnPose(json["data"]);
                break;
            case "arm":
                OnArm(json["data"]);
                break;
            case "battery":
                OnBattery(json["data"]);
                break;
            default:
                throw new Exception($"Unexpected message type: {json["type"]}");
        }
    }

    public void Connect(Mode mode) {
        Debug.LogFormat("try to connect in mode {0}", mode);
        _webSocket.Send($"{{\"type\":\"connect\", \"mode\":{(int)mode}}}");
    }

    public void Vibrate(int value) {
        _webSocket.Send($"{{\"type\":\"vibrate\", \"value\":{value}}}");
    }

    public void SetLEDs(Color logo, Color line) {
        _webSocket.Send($"{{\"type\":\"set_leds\", \"logo\":{logo}, \"line\":{line}}}");
    }

    int[] emgs;
    
    // {"type": "emg", "data": [70, 136, 438, 155, 43, 51, 125, 94]}
    void OnEMG(JToken data) {
        emgs = data.Values<int>().ToArray();
    }
    
    // {"type": "imu", "data": [-8658, 2485, -1778, 13569]}
    void OnIMU(JToken data) {}
    
    
    void OnPose(JToken data) {}
    
    
    void OnArm(JToken data) {}
    
    
    void OnBattery(JToken data) {}
}

