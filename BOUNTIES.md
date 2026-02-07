# 🏴‍☠️ UAL Bounty Board

**Status**: Active
**Total Pool**: Unlimited Glory (and potential future tokens)

This board lists high-priority tasks for the UAL ecosystem. These are "Good First Issues" designed to help you understand the architecture.

## 🎯 Active Bounties

### Task A: Drone Racing Atlas Extension
*   **Difficulty**: ⭐⭐
*   **Description**: The current Atlas lacks high-speed racing maneuvers. We need a specialized dictionary for competitive drone racing.
*   **Deliverable**: A new `racing_v1.yaml` package.
*   **Requirements**:
    *   Define actions like `power_loop`, `split_s`, `rubik_cube`, `barrel_roll`.
    *   Define parameters for `g_force`, `angle_of_attack`, `gate_id`.
    *   Map them to the `0x200-0x250` range.
*   **Tags**: `atlas`, `yaml`, `drone`

### Task B: C# Decoder for Unity
*   **Difficulty**: ⭐⭐⭐
*   **Description**: We need to simulate UAL agents in Unity 3D. A lightweight C# decoder is required to parse UAL binary packets inside Unity scripts.
*   **Deliverable**: A `UALDecoder.cs` class.
*   **Requirements**:
    *   Must run in standard Unity C# environment (Mono).
    *   Input: `byte[]` (UAL binary packet).
    *   Output: `UALInstruction` object (C# struct/class).
    *   Zero-allocation optimization preferred.
*   **Tags**: `csharp`, `unity`, `decoder`

### Task C: Real-time Logic Verification Animation
*   **Difficulty**: ⭐⭐⭐⭐
*   **Description**: The UAL Studio needs to visualize the *flow* of logic. When a user connects `If -> Then`, we want to see a "pulse" animation verifying the logic is valid.
*   **Deliverable**: React component update in `ual-studio/frontend`.
*   **Requirements**:
    *   When the "RUN" button is clicked, animate a signal traveling through the edges.
    *   Green pulse for valid paths, Red pulse for logic errors.
    *   Integration with ReactFlow edges.
*   **Tags**: `frontend`, `react`, `visualization`

---

## How to Claim
1.  Copy the Task Title.
2.  Open a new Issue using the **[Bounty Claim]** template.
3.  Paste the title and describe your plan.
4.  Wait for assignment before starting code.
