# LoadstringIris

bundled version of [birMallard/Iris](https://github.com/SirMallard/Iris) for exploit/loadstring usage.

## usage

```lua
local Iris = loadstring(game:HttpGet("https://raw.githubusercontent.com/Hawkking-cloud/LoadstringIris/main/iris_bundle.lua"))().Init(game.CoreGui)
```

## bundling it yourself

```bash
git pull upstream main
python bundler.py
```
