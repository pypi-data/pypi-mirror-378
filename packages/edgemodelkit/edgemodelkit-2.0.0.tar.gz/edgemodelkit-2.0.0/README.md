# **EdgeModelKit**: Sensor Data Acquisition and Logging Library

EdgeModelKit is a Python library developed by **EdgeNeuron**, designed to simplify sensor data acquisition, logging, and real-time processing for IoT devices. It works seamlessly with the **DataLogger script** from the [EdgeNeuron Arduino library](https://github.com/ConsentiumIoT/EdgeNeuron), and now supports **HTTP-based acquisition** for devices that expose REST APIs.  

---

## **Features**

- **Serial Communication**: Acquire data from devices connected via serial ports.  
- **HTTP Communication**: Fetch data directly from devices exposing REST APIs.  
- **Flexible Data Fetching**: Retrieve sensor data as Python lists or NumPy arrays.  
- **Customizable Logging**: Log sensor data into CSV files with optional timestamps and counters.  
- **Class-Based Organization**: Log data with class labels to prepare datasets for machine learning tasks.  
- **Custom Preprocessing**: Apply custom preprocessing functions to sensor data before logging or inference.  
- **Error Handling**: Gracefully handles data decoding errors, missing keys, or network errors.  

---

## **Usage Prerequisites**

This library is designed to work with devices that provide structured JSON sensor data either:  
1. Over **Serial**, using the **DataLogger script** in the [EdgeSense Arduino library](https://github.com/ConsentiumIoT/EdgeSense).  
2. Over **HTTP**, where the device exposes a REST API returning JSON sensor data.  

---

## **Installation**

```bash
pip install edgemodelkit
````

---

## **Quick Start**

### **1. Initialize the DataFetcher**

#### Serial Mode:

```python
from edgemodelkit import DataFetcher

# Initialize for Serial communication
fetcher = DataFetcher(source="serial", serial_port="COM3", baud_rate=9600)
```

#### HTTP Mode:

```python
from edgemodelkit import DataFetcher

# Initialize for HTTP communication
fetcher = DataFetcher(source="http", api_url="http://192.168.26.123")
```

---

### **2. Fetch Sensor Data**

```python
# Fetch data as a Python list
sensor_data = fetcher.fetch_data(return_as_numpy=False)
print("Sensor Data:", sensor_data)

# Fetch data as a NumPy array
sensor_data_numpy = fetcher.fetch_data(return_as_numpy=True)
print("Sensor Data (NumPy):", sensor_data_numpy)
```

---

### **3. Log Sensor Data**

```python
# Log 10 samples with timestamp and count columns
fetcher.log_sensor_data(class_label="ClassA", num_samples=10, add_timestamp=True, add_count=True)
```

CSV files are saved under a folder named `Dataset`, with subfolders organized by `class_label`.

---

## **CSV Logging Details**

The generated CSV file is named after the sensor (e.g., `TemperatureSensor_data_log.csv`) and includes:

* **Timestamp** (optional)
* **Sample Count** (optional)
* **Data Columns** (`data_value_1`, `data_value_2`, …)

---

## **Real-Time Data Processing Example**

```python
from edgemodelkit import DataFetcher

# Works with both Serial and HTTP
fetcher = DataFetcher(source="http", api_url="http://192.168.26.123")

def custom_preprocess(data):
    # Example: Normalize the data
    return (data - min(data)) / (max(data) - min(data))

try:
    while True:
        sensor_data = fetcher.fetch_data(return_as_numpy=True)
        print("Received Data (Raw):", sensor_data)

        processed_data = custom_preprocess(sensor_data)
        print("Preprocessed Data:", processed_data)

        # prediction = model.predict(processed_data)
        # print("Prediction:", prediction)
finally:
    fetcher.close_connection()
```

---

## **Using ModelPlayGround**

### **1. Initialize and Load Model**

```python
from edgemodelkit import ModelPlayGround

playground = ModelPlayGround()
playground.load_model(model_path="path_to_your_model.keras")
```

### **2. Model Summary and Stats**

```python
playground.model_summary()
playground.model_stats()
```

### **3. Convert Model to TFLite**

```python
playground.model_converter(quantization_type="default")
playground.model_converter(quantization_type="float16")
playground.model_converter(quantization_type="int8")
```

### **4. Test TFLite Model on Live Data**

```python
from edgemodelkit import DataFetcher

fetcher = DataFetcher(source="serial", serial_port="COM3", baud_rate=9600)

def custom_preprocess(data):
    return (data - min(data)) / (max(data) - min(data))

playground_output = playground.edge_testing(
    data_fetcher=fetcher,
    preprocess_func=custom_preprocess
)
print("Model Prediction:", playground_output['ModelOutput'])
print("Sensor data: ", playground_output['SensorData'])
```

### **5. Test with an Existing TFLite Model**

```python
playground_output = playground.edge_testing(
    tflite_model_path="path_to_tflite_model.tflite",
    data_fetcher=fetcher,
    preprocess_func=custom_preprocess
)
print("Model Prediction:", playground_output['ModelOutput'])
print("Sensor data: ", playground_output['SensorData'])
```

---

## **Disclaimer**

Currently, the `ModelPlayGround` class supports `.keras` models for conversion and testing. Support for additional formats may be added in future updates.

---

## **Contributing**

We welcome contributions! Submit bug reports, feature requests, or pull requests at [GitHub](https://github.com/ConsentiumIoT/edgemodelkit).

---

## **License**

MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Support**

📧 [support@edgeneuronai.com](mailto:support@edgeneuronai.com)
🌐 [GitHub Repository](https://github.com/ConsentiumIoT/edgemodelkit)

---

## **About EdgeNeuron**

EdgeNeuron is a pioneer in edge computing solutions, enabling developers to build intelligent IoT applications with state-of-the-art tools and libraries. Learn more at [edgeneuronai.com](https://edgeneuronai.com).

```

---

Do you want me to also include a **feature comparison table (Serial vs HTTP)** in this README to make the new dual-source support stand out?
```
