# Laravel path highlighter

Plugin for Sublime Text 3.

## Features

### Highlights laravel paths

* Highlights paths like `backpack::crud.partials.xxx`
* Provides a command to open such a file (can be triggered by click or shortcut)

## Key binding

```User/Default (Linux).sublime-keymap
{ "keys": ["ctrl+alt+enter"], "command": "open_laravel_path_under_cursor" }
```

## Mouse binding

```User/Default (Linux).sublime-mousemap
[
    {
        "button": "button1",
        "count": 1,
        "modifiers": ["ctrl"],
        "press_command": "drag_select",
        "command": "open_laravel_path_under_cursor"
    }
]
```
