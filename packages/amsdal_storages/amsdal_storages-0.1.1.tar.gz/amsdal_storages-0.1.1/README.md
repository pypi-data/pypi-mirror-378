# amsdal_storages

This plugin provides implementations of the Storage backends for AMSDAL.

## Plugin Structure

- `pyproject.toml` - Plugin configuration file
- `config.yml` - Configuration for connections

## Installing this Plugin

To use this plugin in an AMSDAL application:

1. Copy the plugin directory to your AMSDAL application
2. Import the models and transactions as needed
3. Register the plugin in your application configuration

## Development

This plugin uses sync mode.

### Adding Models

```bash
amsdal generate model ModelName --format py
```

### Adding Properties

```bash
amsdal generate property --model ModelName property_name
```

### Adding Transactions

```bash
amsdal generate transaction TransactionName
```

### Adding Hooks

```bash
amsdal generate hook --model ModelName on_create
```

## Testing

Test your plugin by integrating it with an AMSDAL application and running the application's test suite.