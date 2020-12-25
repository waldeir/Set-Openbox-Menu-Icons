# Set Openbox Menu Icons

Program to set icons to your custom openbox menu.

![](demo.gif)

## Usage


To show icons next to menu entries, it will be necessary to enabled them in the
`<menu>` section of the `~/.config/openbox/rc.xml` file with:

```xml
<showIcons>yes</showIcons>
```

Download the file and run

```
./setopmicons.py
```

It will try to find the icons for each of your menu itens and set them to your
`menu.xml`. If a particular icon is not found, the script will ask to enter
an alternative icon name to look for.
