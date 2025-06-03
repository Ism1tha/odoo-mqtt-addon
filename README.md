# 🚀 Odoo MQTT Integration Module

![MQTT Integration Preview](https://i.imgur.com/VZcKDRJ.png)

> ⚠️ **Educational Project** - This project is designed for self-education and learning purposes. It may be unfinished, contain bugs, or have breaking changes. Not intended for production use.

An Odoo addon module that enables MQTT integration capabilities for manufacturing processes, connecting Odoo manufacturing orders with external MQTT-enabled devices and systems.

> **Related Project**: [Odoo MQTT API](https://github.com/ism1tha/odoo-mqtt-api) - The Node.js API that works with this Odoo module

---

## 📦 What's Inside

- **MQTT Integration Models**: Extended manufacturing models with MQTT capabilities
- **Robot Management**: Configure and manage MQTT-enabled robots
- **Manufacturing Integration**: Connect production orders with external devices
- **Real-time Communication**: MQTT-based task assignment and status tracking
- **Configuration Settings**: Easy setup through Odoo's settings interface
- **Demo Data**: Sample products and materials for quick testing

---

## 🚀 Quick Setup

### 1. Download the Release

Download the latest release from the [GitHub releases page](https://github.com/Ism1tha/odoo-mqtt-addon/releases) or clone the repository:

```bash
git clone git@github.com:Ism1tha/odoo-mqtt-addon.git
```

### 2. Install the Module

1. Copy the `mqtt_integration` folder to your Odoo addons directory
2. Restart your Odoo server
3. Go to **Apps** and search for "MQTT Integration"
4. Click **Install**

### 3. Configure MQTT Settings

1. Go to **Settings > MQTT**
2. Configure your MQTT API connection details:
   - API Host (e.g., localhost)
   - API Port (e.g., 3000)
   - Authentication settings if enabled
3. Save the configuration

### 4. Set up Work Centers and Robots

1. Go to **Manufacturing > Configuration > Work Centers**
2. Edit or create a work center
3. In the **Robots** tab, add MQTT-enabled robots with their topics
4. Save the work center configuration

### 5. Import Demo Data (Optional)

For testing purposes, you can import the provided demo data:

1. Navigate to **Inventory > Products**
2. Go to **Favorites > Import records**
3. Import the CSV files in order:
   - `demo_data/demo_data_1.csv` (Actions)
   - `demo_data/demo_data_2.csv` (Result Products)
   - `demo_data/demo_data_3.csv` (Materials)

---

## 📊 Configuration Overview

| Setting                   | Description                           | Default     |
| ------------------------- | ------------------------------------- | ----------- |
| `MQTT API Host`           | Hostname or IP of the MQTT API server | `localhost` |
| `MQTT API Port`           | Port number for the MQTT API server   | `3000`      |
| `Enable Authentication`   | Enable Bearer token authentication    | `false`     |
| `Authentication Password` | Password for API authentication       | -           |

---

## 📋 Product Types

| Type       | Description                                         |
| ---------- | --------------------------------------------------- |
| `Action`   | Transport action products that trigger MQTT tasks   |
| `Result`   | Products that result from MQTT processing           |
| `Material` | Raw materials with binary data for robot processing |

---

## 🤖 Robot Communication Protocol

### Task Assignment (Odoo → API → Robot)

When a manufacturing order starts, the module sends tasks to the MQTT API:

```json
{
  "taskId": "uuid-generated-id",
  "productionId": 123,
  "robotTopic": "robot1",
  "binaryPayload": "base64_encoded_data"
}
```

### Status Updates (Robot → API → Odoo)

Robots send status updates that are processed by Odoo:

```json
{
  "status": "SUCCESS|ERROR|PROCESSING",
  "timestamp": "2024-01-01T12:00:00Z",
  "completedTaskId": "uuid-task-id"
}
```

---

## 🛠️ Usage

### Setting up Work Centers with Robots

1. Go to **Manufacturing > Configuration > Work Centers**
2. Edit or create a work center
3. In the **Robots** tab:
   - Add robots with unique names
   - Set MQTT topics for each robot
   - Configure robot-specific settings
4. Save the work center configuration

### Configuring MQTT Products

1. Go to **Inventory > Products**
2. Edit a product and go to the **MQTT** tab
3. Set the MQTT Product Type:
   - **Action**: For transport/trigger products
   - **Result**: For products created by robots
   - **Material**: For raw materials with binary data
4. For materials, configure:
   - MQTT Material Binary (binary representation)
   - Result Product (what the robot produces)
   - Result Product Quantity

### Creating Manufacturing Orders

1. Create manufacturing orders for MQTT-enabled products
2. Click **Start MQTT Processing** instead of standard buttons
3. Select a robot from available options
4. The system handles communication with the MQTT API automatically

---

## 🧪 Testing with Demo Data

The module includes demo data to test MQTT functionality:

1. **Actions (demo_data_1.csv)**: Transport action products
2. **Results (demo_data_2.csv)**: Products that robots can create
3. **Materials (demo_data_3.csv)**: Raw materials with binary codes

Each material has a unique binary representation and produces a specific result product when processed by robots.

---

## 🔗 Integration with MQTT API

This module works seamlessly with the [Odoo MQTT API](https://github.com/ism1tha/odoo-mqtt-api):

1. Install and configure this Odoo module
2. Set up the Node.js MQTT API server
3. Configure both to connect to the same MQTT broker
4. Set the correct API host and port in Odoo settings
5. Manufacturing orders will automatically communicate with external robots

---

## 🆘 Troubleshooting

- **Module not appearing in Apps**: Check that the module is in the correct addons directory and restart Odoo
- **MQTT settings not visible**: Go to **Settings > General Settings** and scroll down to find the MQTT section
- **API connection fails**: Verify the MQTT API server is running and check host/port settings
- **Robots not available**: Ensure robots are configured in the work center's **Robots** tab
- **Tasks not being sent**: Check that products have the correct MQTT Product Type configured
- **Import errors with demo data**: Ensure the Manufacturing module is installed before importing CSV files

---

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

---

**Happy Manufacturing! 🏭✨**
