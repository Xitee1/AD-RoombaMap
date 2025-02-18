# AD-RoombaMap

This app generates a map of the cleaned area for supported vacuums with the help of the [iRobot HomeAssistant](https://www.home-assistant.io/integrations/roomba/) integration.
To check if your iRobot vacuum is supported, have a look at its attributes and look for "Position". 

_This project is still in an early state. It should work but there might still be bugs. Make sure to report them :smile:_

## Preview
<img src="https://github.com/user-attachments/assets/4c6403d3-4c7d-463f-8883-17550c32da9e" height="300"><br>

Please note that this App cannot create a floor plan. You need to provide it yourself.
It only draws the red line to indicate where the robot has traveled.

_In this preview, I'm using the [Lovelace Vacuum Map](https://github.com/PiotrMachowski/lovelace-xiaomi-vacuum-map-card) card for a nice combined view of map, controls and sensors._

<br>


## Tested & works with:
- **Roomba 980**

_Your robot is not listed here? Open an issue and tell us if it works with your model :smile:_

<br>

## TODO:
- Overall improvements
- Release on HACS
- Error handling for missing/wrong arguments

<br>

## App configuration
### Important
This app requires the python package `pillow`. You need to install it before using this app!<br>
[Read more about how to install custom packages.](https://github.com/Xitee1/AppDaemon-useful-apps/blob/main/INSTALL_PY_PACKAGES.md)

### Example
```yaml
RoombaMap_roomba:
  module: RoombaMap
  class: Generate
  debug: True
  vacuum_entity: vacuum.roomba
  map_base_image: /homeassistant/floorplans/home.png
  map_offset_x: 200
  map_offset_y: 130
  map_rotation: 90
  tmp_path: /homeassistant/www/tmp
```
_Note: If your addon version is 0.14.0 or below, you should either update or use `config` instead of `homeassistant` in the file paths!_

### Parameters
| key              | required | type   | default | description                                                                                                                        |
|------------------|----------|--------|---------|------------------------------------------------------------------------------------------------------------------------------------|
| `debug`          | False    | bool   | `False` | Enable debug log messages.                                                                                                         |
| `vacuum_entity`  | True     | string |         | The entity_id of the vacuum. Make sure the entity has the "Position" attribute!!                                                   |
| `map_base_image` | True     | string |         | Path to a floor plan of the cleaning area.                                                                                         |
| `map_offset_x`   | True     | int    |         | X offset for the map. Start by setting it to 0. If the lines are out-of-place, change the value (in pixels) to align it correctly. |
| `map_offset_y`   | True     | int    |         | Y offset for the map. Start by setting it to 0. If the lines are out-of-place, change the value (in pixels) to align it correctly. |
| `map_rotation`   | True     | int    |         | Rotate the map if it doesn't align correctly. Start by setting it to 0 and begin trying with 90, 180, 270 to align it.             |
| `tmp_path`       | True     | string |         | A path to a folder that should be used for temp storage. In this path, the map image will be generated for you to be used in HA.   |

### Integrate the generated image into HA
To show the image in HA, just create a new camera with the platform `local_file`.<br>
**Example:**
```yaml
camera:
  - platform: local_file
    name: Roomba Map
    file_path: /config/www/tmp/vacuum_roomba/map.png
```
