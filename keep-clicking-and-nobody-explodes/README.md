# Keep Clicking and Nobody Explodes

A one-page expert helper for Keep Talking and Nobody Explodes, for the
standard rule set (manual version 1, verification code 241).

## Why this exists

For fun, I decided to write a web-based app to not only keep track of various
elements for each bomb (battery, serial, etc.), but to help solve most of the
puzzles as well by various shortcuts. The expert enters what the defuser reads
out and the page gives the answer, with no flipping through the manual.

## What is inside

```text
index.html     the whole page
js/*_241.js    one solver per module
css/           page styles and the jQuery UI theme
js/jquery*, js/d3.min.js   bundled libraries
```

The top of the page holds the bomb's details: serial number vowel and last
digit, battery count, parallel port, the CAR and FRK indicators and the strike
count. Below that is one panel for each of twelve modules: Simple Wires,
Button, Symbols (Keypads), Simon Says, Who's on First, Memory, Morse Code,
Complex Wires, Wire Sequences, Mazes, Passwords and Knobs.

## Use

Open `index.html` in a browser. Nothing is installed or built and nothing is
sent anywhere. Set the bomb's details once, pick a module, enter what the
defuser describes and press Solve.

For example, in Simple Wires with three wires red, blue, blue, the page
answers `Cut the Last Blue Wire.`

## Status and limits

- Checked in November 2026 in a current browser: the page loads, all twelve
  panels appear and the Simple Wires solver gives the manual's answers for the
  cases tried. The other eleven solvers were not re-checked case by case.
- It covers the standard manual only. Other rule seeds and modded modules are
  not handled.
- One background texture of the jQuery UI theme is missing from `css/images`,
  so some buttons are a flat colour. Nothing else depends on it.

## Credits

Keep Talking and Nobody Explodes is by Steel Crate Games. This page is a fan
tool and uses nothing from the game.

Bundled libraries, each under its own licence: jQuery 1.11.3 and jQuery UI
1.11.4 (jQuery Foundation, MIT) and D3 version 3 (Mike Bostock, BSD
3-Clause; text in `js/d3.LICENSE`).
