import os
import time
import json
import tqdm
import requests
import serial
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf


def _process_packet(raw_packet, sensor_data_records, sample_index, add_timestamp, add_count):
    sensor_values = raw_packet.get("sensorValues", [])
    sensor_record = {}
    if add_timestamp:
        sensor_record["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if add_count:
        sensor_record["sample_count"] = sample_index + 1
    sensor_record.update({f"data_value_{i + 1}": value for i, value in enumerate(sensor_values)})
    sensor_data_records.append(sensor_record)


def ensure_directory_exists(dir_path):
    os.makedirs(dir_path, exist_ok=True)


class DataFetcher:
    def __init__(self, source="serial", serial_port=None, baud_rate=9600, api_url=None):
        """
        Parameters:
            source: "serial" or "http"
            serial_port: Serial port (if using serial)
            baud_rate: Baud rate (if using serial)
            api_url: API endpoint (if using http)
        """
        self.source = source
        self.api_url = api_url
        self.serial_connection = None

        if self.source == "serial":
            if not serial_port:
                raise ValueError("serial_port must be provided when using source='serial'")
            self.serial_connection = serial.Serial(port=serial_port, baudrate=baud_rate)

    def close_connection(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Serial connection closed.")

    def _read_packet(self):
        """Read one packet depending on source"""
        if self.source == "serial":
            return json.loads(self.serial_connection.readline().decode())
        elif self.source == "http":
            r = requests.get(self.api_url, timeout=5)
            return r.json()
        else:
            raise ValueError("Unsupported source. Use 'serial' or 'http'.")

    def fetch_data(self, return_as_numpy=False):
        try:
            raw_packet = self._read_packet()
            values = raw_packet.get("sensorValues", [])
            return np.array(values) if return_as_numpy else values
        except (json.JSONDecodeError, KeyError, requests.RequestException) as e:
            print(f"Error fetching data: {e}")
            return np.array([]) if return_as_numpy else []

    def log_sensor_data(self, class_label=None, num_samples=5, add_timestamp=False, add_count=False, output_dir="."):
        initial_packet = self._read_packet()
        sensor_name = initial_packet.get("sensorName", "Unknown")
        file_name = f"{sensor_name}_data_log.csv"

        # Choose dataset folder
        if class_label:
            directory_path = os.path.join("Dataset", str(class_label))
        else:
            directory_path = "Dataset"

        ensure_directory_exists(directory_path)

        output_file_name = os.path.join(directory_path, file_name)

        sensor_data_records = []
        _process_packet(initial_packet, sensor_data_records, sample_index=0,
                        add_timestamp=add_timestamp, add_count=add_count)

        print(f"Sampling {sensor_name} sensor.")

        for sample_index in tqdm.tqdm(range(1, num_samples), desc="Gathering data", unit="samples"):
            raw_packet = self._read_packet()
            _process_packet(raw_packet, sensor_data_records, sample_index,
                            add_timestamp=add_timestamp, add_count=add_count)

        data_frame = pd.DataFrame(sensor_data_records)
        data_frame.to_csv(output_file_name, index=False)
        print(f"\nData saved to {output_file_name}")


def load_scaler(scaler_file):
    scaler = joblib.load(scaler_file)
    return scaler.mean_.tolist(), scaler.scale_.tolist()


def _convert_tflite_to_c_array(tflite_file):
    with open(tflite_file, 'rb') as f:
        tflite_data = f.read()

    tflite_length = len(tflite_data)

    # Convert binary data to a formatted C array
    hex_lines = [', '.join([f'0x{byte:02x}' for byte in tflite_data[i:i + 12]])
                 for i in range(0, len(tflite_data), 12)]

    # Ensure consistent indentation by joining lines
    formatted_c_array = ',\n    '.join(hex_lines)

    return formatted_c_array, tflite_length


def _format_scaler_with_new_lines(data, values_per_line=5):
    # Split the data into chunks of specified size
    lines = [', '.join([str(x) for x in data[i:i + values_per_line]])
             for i in range(0, len(data), values_per_line)]
    # Join the chunks with newline
    return ',\n    '.join(lines)


def _append_to_model_h(model_header_file, scaler_mean, scaler_scale, tflite_array, tflite_length):
    model_h_file_name = os.path.splitext(os.path.basename(model_header_file))[0]

    # Prepare the scaler data if available
    scaler_section = ""
    if scaler_mean is not None and scaler_scale is not None:
        scaler_mean_str = _format_scaler_with_new_lines(scaler_mean, values_per_line=5)
        scaler_scale_str = _format_scaler_with_new_lines(scaler_scale, values_per_line=5)

        scaler_section = f"""
// Scaler Data
// -----------------------------
// Mean and scale values extracted from scaler.pkl
// These are used for preprocessing input data before inference.
const float scaler_mean[] = {{
    {scaler_mean_str}
}};

const float scaler_scale[] = {{
    {scaler_scale_str}
}};
"""

    # Prepare the content for model.h
    model_h_content = f"""/*
 * EdgeNeuron Model Header File
 * ---------------------------------------------
 * This header file is auto-generated by EdgeNeuronAI,
 * a platform specializing in TinyML for edge devices.
 *
 * It contains both the TensorFlow Lite (TFLite) model data
 * and the scaler details for preprocessing (if available).
 *
 * Usage: Deploy this header file on your microcontroller or
 * edge device to enable real-time inference with the EdgeNeuron framework.
 */

#ifndef EDGE_NEURON_MODEL_H
#define EDGE_NEURON_MODEL_H

// TFLite Model Data
// -----------------------------
// Generated from: {model_h_file_name}.tflite
// Note: Ensure this model aligns with the input/output structure 
// expected by your edge application.
unsigned char {model_h_file_name}[] = {{
    {tflite_array}
}};
unsigned int {model_h_file_name}_len = {tflite_length};

{scaler_section}

#endif  // EDGE_NEURON_MODEL_H
"""

    # Write the content to model.h
    with open(model_header_file, 'w') as f:
        f.write(model_h_content)


class ModelPlayGround:
    def __init__(self):
        self.scaler_scale = None
        self.scaler_mean = None
        self.scaler_used = None
        self.tflite_model_path = None
        self.output_details = None
        self.input_details = None
        self.interpreter = None
        self.loaded_model = None
        self.model_path = None

    def load_model(self, model_path: str):
        self.model_path = model_path
        self.loaded_model = tf.keras.models.load_model(self.model_path)

    def model_summary(self):
        self.loaded_model.summary()

    def model_stats(self):
        model_size = os.path.getsize(self.model_path) / 1024  # Size in KB
        print(f"Model Size: {model_size:.2f} KB")
        print(f"Number of Parameters: {self.loaded_model.count_params()}")

    def model_converter(self, quantization_type = "default"):
        saved_tflite_model_dir = "saved-model/tflite-models/"
        ensure_directory_exists(saved_tflite_model_dir)

        base_model_name = os.path.splitext(os.path.basename(self.model_path))[0]

        def save_tflite_model(tflite_model, file_suffix):
            output_file_name = os.path.join(saved_tflite_model_dir, f"{base_model_name}_{file_suffix}.tflite")
            with open(output_file_name, 'wb') as f:
                f.write(tflite_model)
            print(f"Saved {file_suffix} model at: {output_file_name}")

        # Default (float32) model
        if quantization_type == "default":
            print("Converting to default (float32) TFLite model...")
            converter = tf.lite.TFLiteConverter.from_keras_model(self.loaded_model)
            tflite_model = converter.convert()
            save_tflite_model(tflite_model, "default")

        # Float16 quantized model
        if quantization_type == "float16":
            print("Converting to float16 TFLite model...")
            converter = tf.lite.TFLiteConverter.from_keras_model(self.loaded_model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tf.float16]
            tflite_model = converter.convert()
            save_tflite_model(tflite_model, "float16")

        # Int8 quantized model
        if quantization_type == "int8":
            print("Converting to int8 TFLite model...")
            converter = tf.lite.TFLiteConverter.from_keras_model(self.loaded_model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]

            # Representative Dataset for int8 Quantization
            def representative_data_gen():
                for _ in range(100):
                    # Generate random data matching the input shape
                    yield [np.random.rand(*self.loaded_model.input_shape[1:]).astype(np.float32)]

            converter.representative_dataset = representative_data_gen
            converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            converter.inference_input_type = tf.uint8  # or tf.int8
            converter.inference_output_type = tf.uint8  # or tf.int8
            tflite_model = converter.convert()
            save_tflite_model(tflite_model, "int8")

    def set_edge_model(self, tflite_model_path):
        self.tflite_model_path = tflite_model_path
        self.interpreter = tf.lite.Interpreter(model_path=self.tflite_model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def edge_testing(self, data_fetcher, preprocess_func=None, debug=False):
        if not hasattr(self, 'interpreter'):
            raise ValueError("Edge model not set. Call `set_edge_model` first.")

        sensor_data = data_fetcher.fetch_data(return_as_numpy=True)
        if sensor_data.size == 0:
            if debug:
                print("No sensor data received.")
            return None

        scaler_mean = None
        scaler_scale = None

        # Apply preprocessing if a function is provided
        if preprocess_func:
            # Analyze the preprocess_func for a scaler
            if hasattr(preprocess_func, "__globals__"):
                func_globals = preprocess_func.__globals__
                for var_name, var_value in func_globals.items():
                    # Check if a StandardScaler or similar instance is present
                    if hasattr(var_value, "mean_") and hasattr(var_value, "scale_"):
                        scaler_mean = var_value.mean_.tolist()
                        scaler_scale = var_value.scale_.tolist()
                        self.scaler_used = True
                        self.scaler_mean = scaler_mean
                        self.scaler_scale = scaler_scale
                        if debug:
                            print(f"Scaler detected: {type(var_value).__name__}")
                        break
                else:
                    self.scaler_used = False
                    self.scaler_mean = None
                    self.scaler_scale = None
            else:
                self.scaler_used = False
                self.scaler_mean = None
                self.scaler_scale = None

            # Apply the preprocessing function
            sensor_data = preprocess_func(sensor_data)

        # Ensure the input shape matches the model's expected input
        input_shape = self.input_details[0]['shape']
        input_data = sensor_data.astype(self.input_details[0]['dtype'])

        if debug:
            print(f"Expected shape is: {input_shape}, provided shape is: {sensor_data.shape}")

        # Set input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

        # Perform inference
        start_time = time.perf_counter()
        self.interpreter.invoke()
        stop_time = time.perf_counter()

        if debug:
            print(f"Inference time: {stop_time - start_time:.6f} seconds")

        # Get prediction
        prediction = self.interpreter.get_tensor(self.output_details[0]['index'])

        return {"SensorData": input_data, "ModelOutput": prediction}

    def export_model(self, scaler_used=None):
        output_dir = "saved-model/tflm-models"
        ensure_directory_exists(output_dir)

        tflite_array, tflite_length = _convert_tflite_to_c_array(self.tflite_model_path)

        # Save the header file
        # model_name = os.path.splitext(os.path.basename(self.tflite_model_path))[0]
        header_file = os.path.join(output_dir, "edge_neuron_model.h")
        if scaler_used:
            scaler_mean = scaler_used.mean_.tolist()
            scaler_scale = scaler_used.scale_.tolist()
            _append_to_model_h(header_file, scaler_mean, scaler_scale, tflite_array, tflite_length)
        else:
            _append_to_model_h(header_file, self.scaler_mean, self.scaler_scale, tflite_array, tflite_length)
        print(f"TFLM model exported to: {header_file}")
