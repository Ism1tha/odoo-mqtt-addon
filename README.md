# MQTT Integration - Odoo MQTT Interface

## Description

This Odoo MQTT addon (`mqtt_integration`) is developed as part of a collaborative project between the **Web Development (DAW)** and **Robotics** specializations at **Institut Montsià**.

It provides an intuitive Odoo interface designed for operators to efficiently manage robots within the system via MQTT. The addon streamlines robot management by offering an organized platform where operators can monitor, control, and configure robots as needed.

- Custom project management tools tailored for DAW and Robotics collaboration.
- Automation features to streamline workflow processes.
- Integration with MQTT for real-time robot communication.
- Odoo interface to generate and manage work orders.
- Modular and extensible architecture for future enhancements.

## Installation

### Option 1: Download from Releases (Recommended)

1. Go to the [Releases](https://github.com/Ism1tha/odoo-mqtt-addon/releases) page.
2. Download the latest `mqtt_integration-x.x.x.zip` file.
3. Extract the zip file to your Odoo `addons` directory.
4. Restart the Odoo server.
5. Activate _Developer Mode_ in Odoo.
6. Go to the **Apps** menu, click _Update Apps List_, and search for "MQTT Integration".
7. Click _Install_ on the **Odoo MQTT Interface** addon.

### Option 2: Manual Installation

1. Go to your Odoo `addons` directory.
2. Create a new folder named `mqtt_integration`.
3. Place the contents of this repository inside that folder.
4. Restart the Odoo server.
5. Activate _Developer Mode_ in Odoo.
6. Go to the **Apps** menu, click _Update Apps List_, and search for "MQTT Integration".
7. Click _Install_ on the **Odoo MQTT Interface** addon.

## Usage

1. Navigate to the **MQTT Integration** section in the Odoo interface.
2. Configure the MQTT settings to connect to the robots.
3. Generate work orders directly through the Odoo interface.
4. Manage the workflow and automate communication with the robots via MQTT.

## Features

- **MQTT Integration**: Real-time communication with manufacturing robots via MQTT protocol.
- **Robot Management**: Configure and monitor robots through the Odoo interface.
- **Production Order Automation**: Automatic MQTT communication for production processes.
- **Work Center Configuration**: Set up MQTT topics for different work centers.
- **Product Template MQTT Settings**: Configure MQTT parameters at the product level.

## Releases

This project uses automated releases through GitHub Actions. When a new tag is pushed to the repository:

1. A new release is automatically created on GitHub.
2. The addon is packaged as `mqtt_integration-{version}.zip`.
3. The release includes all necessary files for easy installation in Odoo.

To stay updated with the latest version, check the [Releases](https://github.com/Ism1tha/odoo-mqtt-addon/releases) page regularly.

## Related Projects

This addon works in conjunction with the **Odoo MQTT API** for complete MQTT integration:

- **[Odoo MQTT API](https://github.com/Ism1tha/odoo-mqtt-api)**: A Node.js/TypeScript API server that handles MQTT communication between Odoo and manufacturing robots. This API provides endpoints for task management, robot simulation, and real-time communication bridging.

## Contribution

Contributions are welcome! If you’d like to improve the addon, please follow these steps:

1. Fork the repository.
2. Create a new branch.
3. Make your modifications and commit.
4. Push to your branch and create a Pull Request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For questions or suggestions, feel free to open an issue or reach out to the project maintainers.
