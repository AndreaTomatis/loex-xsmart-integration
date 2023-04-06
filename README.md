# Loex Xsmart Integration for Home Assistant

A full-featured Homeassistant component to drive Loex Xsmart Devices

## Installation

You can install this component in two ways: via HACS or manually.
HACS is a nice community-maintained components manager, which allows you to install git-hub hosted components in a few clicks.
If you have already HACS installed on your HomeAssistant, it's better to go with that.
On the other hand, if you don't have HACS installed or if you don't plan to install it, then you can use manual installation.

### Option A: Installing via HACS
If you have HACS, you need first to add the repository in HACS. Then, just search for "Loex" (Full name is Loex Xsmart Integration) in the default repository of HACS and it'll show up. Click on Install. When the installation completes, **you must restart homeassistant** in order to make it work.

### Option B: Classic installation (custom_component)
1. Download the latest zip release archive
1. Unzip/copy the directory within the `custom_components` directory of your homeassistant installation.
The `custom_components` directory resides within your homeassistant configuration directory.
Usually, the configuration directory is within your home (`~/.homeassistant/`).
In other words, the configuration directory of homeassistant is where the config.yaml file is located.
After a correct installation, your configuration directory should look like the following.
    ```
    └── ...
    └── configuration.yaml
    └── custom_components
        └── loex_xsmart
            └── __init__.py
            └── ...
    ```

    **Note**: if the custom_components directory does not exist, you need to create it.

After copy-pasting the loex_xsmart directory into the custom_components folder, you need to restart HomeAssistant.

# Disclaimer

Author is in no way affiliated with Loex.

Author does not guarantee functionality of this integration and is not responsible for any damage.

All product names, trademarks and registered trademarks in this repository, are property of their respective owners.