---
name: glove80-zmk-configuration
description: Help with ZMK firmware configuration, specifically for Glove80, including keymap syntax, behaviors, and devicetree structure. Use when editing .keymap files or configuring keyboard behaviors.
---

# Glove80 ZMK Configuration

Detailed instructions for configuring ZMK firmware for the Glove80 keyboard.

## When to Use

- Use this skill when editing `.keymap` files (e.g., `config/glove80.keymap`).
- Use this skill when configuring ZMK behaviors (layers, macros, tap-dances, hold-taps).
- Use this skill when interpreting devicetree syntax errors in ZMK configurations.
- Use this skill when looking up ZMK key codes or behavior syntax.

## Instructions

### Keymap Structure
ZMK uses a **declarative devicetree** syntax. The main file is usually `config/glove80.keymap`.

The keymap file structure generally follows this pattern:

```dts
// Includes
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

// Root definition
/ {
    // Custom behaviors (macros, tap-dances, hold-taps)
    behaviors {
        // ...
    };

    // Macros
    macros {
        // ...
    };

    // Keymap layers
    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                // 80 bindings for Glove80
                &kp Q  &kp W  ...
            >;
        };
    };
};
```

### Common Behaviors

| Behavior | Syntax | Description |
| :--- | :--- | :--- |
| **Key Press** | `&kp CODE` | Standard key press (e.g., `&kp A`, `&kp LSHIFT`). |
| **Momentary Layer** | `&mo LAYER` | Activate layer while held. |
| **Mod-Tap** | `&mt MOD KEY` | Modifier when held, Key when tapped (e.g., `&mt LCTRL ESC`). |
| **Layer-Tap** | `&lt LAYER KEY` | Layer when held, Key when tapped. |
| **Sticky Key** | `&sk MOD` | Modifier stays active until next key press. |
| **Toggle Layer** | `&tog LAYER` | Toggle layer on/off. |
| **To Layer** | `&to LAYER` | Switch to layer (deactivates others). |
| **Transparent** | `&trans` | Pass event to lower active layer. |
| **None** | `&none` | No action. |

### Glove80 Layout Details
- The Glove80 has **80 keys**. The `bindings` array in each layer MUST have exactly 80 entries.
- **Finger Cluster**: 6 columns x 4 rows per hand.
- **Thumb Cluster**: 6 keys per hand (arranged in arcs).

### Custom Behaviors

#### Macro
```dts
macros {
    ZMK_MACRO(my_macro,
        wait-ms = <30>;
        tap-ms = <40>;
        bindings = <&kp H &kp E &kp L &kp L &kp O>;
    )
};
```

#### Tap Dance
```dts
behaviors {
    td0: tap_dance_0 {
        compatible = "zmk,behavior-tap-dance";
        #binding-cells = <0>;
        tapping-term-ms = <200>;
        bindings = <&kp N1>, <&kp N2>, <&kp N3>; // Tap 1x, 2x, 3x
    };
};
```

#### Hold-Tap (Custom)
```dts
behaviors {
    lh_pht: left_hand_positional_hold_tap {
        compatible = "zmk,behavior-hold-tap";
        #binding-cells = <2>;
        flavor = "tap-preferred";
        tapping-term-ms = <200>;
        bindings = <&kp>, <&kp>;
        hold-trigger-key-positions = < ... >; // Keys that trigger hold
    };
};
```

### Best Practices and Tips

1.  **Check Syntax**: Ensure every opening `<` has a closing `>` and every `{` has a `};`.
2.  **Includes**: Make sure you include necessary headers (e.g., `#include <dt-bindings/zmk/bt.h>` for Bluetooth).
3.  **Comments**: Use `//` for single line or `/* ... */` for block comments.
4.  **Key Codes**: Refer to `dt-bindings/zmk/keys.h` for valid key codes (e.g., `N1`, `A`, `SPACE`, `RET`).

### Resources

- [ZMK Codes](https://zmk.dev/docs/codes)
- [ZMK Behaviors](https://zmk.dev/docs/behaviors)
