# AD-RoombaMap

This app generates a map of the cleaned area for supported vacuums, from the iRobot HA integration.
To check if your iRobot vacuum is supported, have a look at its attributes and look for "Position". 

### Tested & works with:
- **Roomba 980**

### Preview
<img src="https://github.com/Xitee1/AppDaemon-useful-apps/assets/59659167/823517c2-d144-49ed-8333-e6b889889b78" height="300">

<br>

### Warning: This project is still under beta development! It should work but expect some bugs and that some things get changed.
**Current state**: Not working - problems with file paths

### TODO:
- Fix file path problems
- Update preview image in readme
- Release on HACS

<br>

## App configuration
### Important
This apps requires the python package `pillow`. You need to install it before using this app!<br>
[Read more about how to install custom packages.](https://github.com/Xitee1/AppDaemon-useful-apps/blob/main/INSTALL_PY_PACKAGES.md)

### Example
```yaml
RoombaMap_roomba:
  module: RoombaMap
  class: Generate
  debug: True
  vacuum_entity: vacuum.roomba
  map_base_image: /config/floorplans/home.png
  map_offset_x: 200
  map_offset_y: 130
  map_rotation: 90
  tmp_path: /config/www/tmp
```

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