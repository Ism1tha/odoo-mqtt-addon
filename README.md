# 🚀 Odoo MQTT Integration - Development Environment

> ⚠️ **Early Access Version** - This project is currently in active development. While functional, it may contain bugs and breaking changes. Use with caution in production environments.

A Docker-based development environment for Odoo with MQTT integration capabilities, designed to help you **kickstart your custom Odoo module development** with minimal setup.

> **Related Project**: [Odoo MQTT API](https://github.com/your-repo/odoo-mqtt-api) - The Node.js API that works with this Odoo environment

---

## 📦 What's Inside

- **Odoo (latest)** with developer mode and auto-update enabled
- **PostgreSQL 15** as the database backend
- **Docker secrets** for safe password management
- **Volume mounts** for configuration, extra addons, and persistent data
- **MQTT Integration Support**: Ready for custom MQTT addon development

---

## 🚀 Quick Setup

### 1. Clone the Repository

```bash
git clone git@github.com:Ism1tha/odoo-environment-template.git
cd odoo-environment-template
```

### 2. Add the PostgreSQL Password Secret

Create a file named `odoo_pg_pass` at the root containing your PostgreSQL password:

```
your_strong_password
```

### 3. Launch the Environment

```bash
docker compose up -d
```

> The first launch might take a bit while images are downloaded and Odoo is initialized.

---

## 📊 Configuration Overview

| Path / Variable   | Description                           | Default           |
| ----------------- | ------------------------------------- | ----------------- |
| `./addons/`       | Your custom Odoo modules go here      | -                 |
| `./config/`       | Optional Odoo configuration directory | -                 |
| `8069`            | Port exposed for accessing Odoo       | `8069`            |
| `demo_enterprise` | Default database name                 | `demo_enterprise` |
| `odoo_pg_pass`    | File containing PostgreSQL password   | -                 |

---

## 📂 Directory Structure

```
.
├── addons/                 # Your custom addons
├── config/                 # (Optional) Odoo config files
├── odoo_pg_pass            # Secret password file
└── docker-compose.yml
```

---

## 🛠️ Developer Mode

The Odoo container runs with:

```bash
odoo -d demo_enterprise --update=all --dev=all
```

This enables:

- Full developer tools
- Auto-update of all modules at startup
- Debug mode for development

---

## 🧪 MQTT Integration Development

This environment is ready for MQTT addon development. To add MQTT capabilities:

1. Install the [Odoo MQTT Integration Addon](https://github.com/Ism1tha/odoo-mqtt-addon)
2. Configure your MQTT broker connection
3. Set up the companion [MQTT API](https://github.com/your-repo/odoo-mqtt-api)

---

## 🧼 Stop & Clean Up

To stop and remove containers, volumes, and networks:

```bash
docker compose down -v
```

---

## 🆘 Troubleshooting

- **Database connection issues**: Check `odoo_pg_pass` file exists and contains the correct password
- **Addon not loading**: Ensure your addon is in `./addons/` directory
- **Port conflicts**: Make sure port 8069 is not already in use
- **Permission issues**: Check Docker has proper permissions to access volumes

---

## 📣 Notes

- Make sure `odoo_pg_pass` is stored safely and not pushed to public repositories
- Odoo will use the `demo_enterprise` database by default
- This setup is **not intended for production** use
- Works seamlessly with the [MQTT API companion project](https://github.com/your-repo/odoo-mqtt-api)

---

## 📄 License

MIT License – do whatever you want, just don't blame me if your Odoo breaks 😉

---

**Happy Coding! 🛠️✨**
