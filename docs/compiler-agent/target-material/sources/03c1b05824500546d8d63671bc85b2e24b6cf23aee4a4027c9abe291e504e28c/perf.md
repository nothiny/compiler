---
sidebar_position: 8
---

# Perf Usage Note

(For basic usage of the perf tool, please refer to the [official tutorial](https://perf.wiki.kernel.org/index.php/Tutorial). This will not be mentioned in this article.)

The current support for perf on RISC-V is related to the following software/hardware frameworks/specifications:

- Linux perf framework
  - The main framework of perf
  - The pmu-events json files in perf (which allow perf to specify specific hardware events by name rather than raw encoding)
- SBI PMU Extension
- RISC-V hardware specifications
  - HPM (Hardware Performance Monitor) defined in RISC-V ISA Privileged Specification
  - Sscofpmf Extension

Their relationship is as follows:

![Linux perf framework on RISC-V](./static/perf-framework-riscv.png)

However, even if all the above are supported in software/hardware, perf users still need to pay attention to:

## How Events Map to Hardware

The "Hardware event" and "Hardware cache event" in `perf list` are names pre-defined by Linux perf framework. On RISC-V, they are connected to the actual HPM hardware counters through the SBI PMU Extension. In the PMU Extension implementation of OpenSBI, this mapping is described in the node with `compatible = "riscv,pmu"`:

- `riscv,event-to-mhpmevent`: event number of perf → selector written into the `mhpmevent` CSR
- `riscv,event-to-mhpmcounters`: range of event numbers → which counters are allowed (bitmap)
- `riscv,raw-event-to-mhpmcounters`: raw selector → which counters are allowed (bitmap)

For detailed description of the format, please refer to the document [docs/pmu_support.md](https://github.com/riscv-software-src/opensbi/blob/master/docs/pmu_support.md) in OpenSBI sources.

**These contents in Device Tree are parsed by OpenSBI, and cannot be noticed by Linux perf framework** (no relevant specifications are defined). Therefore:

- not every hardware event listed in `perf list` corresponds to an actual HPM event;
- the same selector may stand for different events on different models of core.

The event tables are not the same across cores. The mappings of X60 and X100 are given in the following sections.

## Not Every Hardware Events in `perf list` is Available

**Symptoms:**

The hardware events listed in `perf list` do not mean that this hardware platform supports all of them.

For example, the output of `perf list` is:

```shell
$ perf list | grep Hardware
  branch-instructions OR branches                    [Hardware event]
  branch-misses                                      [Hardware event]
  bus-cycles                                         [Hardware event]
  cache-misses                                       [Hardware event]
  cache-references                                   [Hardware event]
  cpu-cycles OR cycles                               [Hardware event]
  instructions                                       [Hardware event]
  ref-cycles                                         [Hardware event]
  stalled-cycles-backend OR idle-cycles-backend      [Hardware event]
  stalled-cycles-frontend OR idle-cycles-frontend    [Hardware event]
  L1-dcache-load-misses                              [Hardware cache event]
  L1-dcache-loads                                    [Hardware cache event]
  L1-dcache-prefetch-misses                          [Hardware cache event]
  L1-dcache-prefetches                               [Hardware cache event]
  L1-dcache-store-misses                             [Hardware cache event]
  L1-dcache-stores                                   [Hardware cache event]
  L1-icache-load-misses                              [Hardware cache event]
  L1-icache-loads                                    [Hardware cache event]
  L1-icache-prefetch-misses                          [Hardware cache event]
  L1-icache-prefetches                               [Hardware cache event]
  LLC-load-misses                                    [Hardware cache event]
  LLC-loads                                          [Hardware cache event]
  LLC-prefetch-misses                                [Hardware cache event]
  LLC-prefetches                                     [Hardware cache event]
  LLC-store-misses                                   [Hardware cache event]
  LLC-stores                                         [Hardware cache event]
  branch-load-misses                                 [Hardware cache event]
  branch-loads                                       [Hardware cache event]
  dTLB-load-misses                                   [Hardware cache event]
  dTLB-loads                                         [Hardware cache event]
  dTLB-prefetch-misses                               [Hardware cache event]
  dTLB-prefetches                                    [Hardware cache event]
  dTLB-store-misses                                  [Hardware cache event]
  dTLB-stores                                        [Hardware cache event]
  iTLB-load-misses                                   [Hardware cache event]
  iTLB-loads                                         [Hardware cache event]
  node-load-misses                                   [Hardware cache event]
  node-loads                                         [Hardware cache event]
  node-prefetch-misses                               [Hardware cache event]
  node-prefetches                                    [Hardware cache event]
  node-store-misses                                  [Hardware cache event]
  node-stores                                        [Hardware cache event]
```

But the counting results of some of them will be `<not counted>`. It could be caused by that these events are not supported in this hardware, or supported but just didn't occur during this counting:

```shell
$ perf stat -e cycles,branches,bus-cycles,ref-cycles ls

 Performance counter stats for 'ls':

           1719370      cycles
             94325      branches
     <not counted>      bus-cycles                                (0.00%)
     <not counted>      ref-cycles                                (0.00%)

       0.002556584 seconds time elapsed

       0.002900000 seconds user
       0.000000000 seconds sys
```

> The above is how older versions of perf behave: they print all events pre-defined by the framework, whether the current platform supports them or not. Newer perf (since Linux 6.0) tries to open each event before listing it, and the events that fail to open are no longer listed.

**Causes:**

As described in the previous section, the mapping between events and hardware is defined in the Device Tree and parsed by OpenSBI, so the perf tool itself cannot know which events the firmware has defined. Therefore, not every hardware event listed in `perf list` corresponds to an actual HPM event.

**How to confirm and read the result:**

To tell the cases apart, look at how the event is displayed in `perf stat`:

| What you see | Meaning | What to do |
|---|---|---|
| The event is not in `perf list` | This perf version probed it, or the firmware defines no mapping for it | Specify it by raw selector (see "How to Use Raw Hardware Events"), or check the firmware version |
| `<not supported>` | The event failed to open, SBI rejected it | Same as above |
| `<not counted>` | The event opened successfully, but its enabled/running time is 0 | Usually because the events being counted exceed the available counters and this one got multiplexed out; count fewer events at the same time |
| A percentage below 100% after the event name | The counter was multiplexed, and the count is scaled from the sampled time | The lower the percentage, the larger the variation |

> `<not supported>` and `<not counted>` come from two different stages: the former is rejected when opened, the latter opened fine but nothing was counted.

## X60

### Events and Counters

This is an example of Device Tree for X60:

```dts
pmu {
    compatible = "riscv,pmu";

    riscv,event-to-mhpmevent =
    /* BRANCH_INSTRUCTIONS */
    <0x00005 0x0 0x01>,
    /* BRANCH_MISSES */
    <0x00006 0x0 0x02>,
    /* STALLED_CYCLES_FRONTEND */
    <0x00008 0x0 0x03>,
    /* STALLED_CYCLES_BACKEND */
    <0x00009 0x0 0x04>,
    /* L1D_READ_ACCESS */
    <0x10000 0x0 0x06>,
    /* L1D_READ_MISS */
    <0x10001 0x0 0x05>,
    /* L1D_WRITE_ACCESS */
    <0x10002 0x0 0x0a>,
    /* L1D_WRITE_MISS */
    <0x10003 0x0 0x09>,
    /* L1I_READ_ACCESS */
    <0x10008 0x0 0x0c>,
    /* L1I_READ_MISS */
    <0x10009 0x0 0x0b>,
    /* L1I_PREFETCH_ACCESS */
    <0x1000c 0x0 0x0e>,
    /* L1I_PREFETCH_MISS */
    <0x1000d 0x0 0x0d>,
    /* DTLB_READ_MISS */
    <0x10019 0x0 0x15>,
    /* DTLB_WRITE_MISS */
    <0x1001b 0x0 0x19>,
    /* ITLB_READ_MISS */
    <0x10021 0x0 0x1b>;

    /* 16 valid counters: mhpmcounter3 ~ mhpmcounter18 */
    riscv,event-to-mhpmcounters =
     <0x00005 0x00006 0x0007fff8>,
     <0x00008 0x00009 0x0007fff8>,
     <0x10000 0x10003 0x0007fff8>,
     <0x10008 0x10009 0x0007fff8>,
     <0x1000c 0x1000d 0x0007fff8>,
     <0x10019 0x10019 0x0007fff8>,
     <0x1001b 0x1001b 0x0007fff8>,
     <0x10021 0x10021 0x0007fff8>;

    riscv,raw-event-to-mhpmcounters =
     /*
      * For convenience, we treat 0x1~0xff as valid indexes,
      * but actually in hardware the valid indexes are 0x1~0xbd.
      */
     <0x0 0x0 0xffffffff 0xffffff00 0x0007fff8>;
};
```

X60 has 16 programmable counters, `mhpmcounter3` to `mhpmcounter18`, and each of the events above may use any of them.

### Sampling (such as `perf record`) for `cycles` or `instructions` Event are Invalid on X60

**Symptoms:**

On X60, the sampling functions in perf (including but not limited to `record`, `top`, etc.), are invalid for `cycles` or `instructions` event. The possible issues include but are not limited to:

- After running `perf record`, executing `perf report` for the generated `perf.data`, the error "The perf.data data has no samples!" occurs:

  ![perf record error - no samples](./static/perf-record-error-no-samples.png)

- There is no output when executing `perf top`.

- ...

**Causes:**

The sampling functions in perf rely on the counters to provide overflow interrupts. On RISC-V, the Sscofpmf Extension defines how the `mhpmevent` counters in hardware provide overflow interrupts.

But for the counter CSRs, `mcycle` and `minstret`, used by `cycles` and `instructions` events, neither of their overflow interrupts is defined in Sscofpmf Extension. X60 doesn't have any additional processing for this. So sampling for the two events doesn't work.

![overflow interrupt of mcycle & minstret not defined in Sscofpmf](./static/perf-framework-sscofpmf-cycle-instret.png)

In most cases, if without `-e` option to specify events, perf will use `cycles` event by default. **Therefore, it is expected that there is no output or result samples are 0 by default when using perf sampling on X60. We can use `-e` option to specify other events and then we will find it works**. For example:

![perf record for branches event](./static/perf-record-branches.png)

Consider to use the following events as an alternative to `cycles` and `instructions` events when using perf sampling to analyse performance on X60:

- Software events such as `cpu-clock`, `task-clock`, etc.
- Specific events supported on X60 hardware, such as U/S/M mode cycles, various intructions, etc. (Please refer to the hardware user manual for more details about these events. For how to use them in perf, please refer to the following section "How to Use Raw Hardware Events".)

## X100

### Events and Counters

The Device Tree mapping of X100 differs from X60's in several places:

- `cycles` and `instructions` are pinned to `mhpmcounter17` and `mhpmcounter18` respectively;
- `stalled-cycles-frontend` / `stalled-cycles-backend` and the L1I prefetch events are gone;
- L1D prefetch events and the DTLB access events are added.

| perf event name | Event number | Selector | Counters used |
|---|---|---|---|
| cycles | 0x00001 | 0x1e | mhpmcounter17 |
| instructions | 0x00002 | 0x1f | mhpmcounter18 |
| branches | 0x00005 | 0x01 | shared |
| branch-misses | 0x00006 | 0x02 | shared |
| L1-dcache-loads | 0x10000 | 0x06 | shared |
| L1-dcache-load-misses | 0x10001 | 0x05 | shared |
| L1-dcache-stores | 0x10002 | 0x0a | shared |
| L1-dcache-store-misses | 0x10003 | 0x09 | shared |
| L1-dcache-prefetches | 0x10004 | 0x08 | shared |
| L1-dcache-prefetch-misses | 0x10005 | 0x07 | shared |
| L1-icache-loads | 0x10008 | 0x0c | shared |
| L1-icache-load-misses | 0x10009 | 0x0b | shared |
| dTLB-loads | 0x10018 | 0x16 | shared |
| dTLB-stores | 0x1001a | 0x1a | shared |
| dTLB-store-misses | 0x1001b | 0x19 | shared |
| iTLB-load-misses | 0x10021 | 0x1b | shared |

"shared" means any of `mhpmcounter3` to `mhpmcounter16`, 14 in total. So at most 14 general events can be counted at the same time on X100; `cycles` and `instructions` do not occupy any of these 14. Anything beyond that is multiplexed.

The following events have no mapping defined on X100 and cannot be used by name: `bus-cycles`, `ref-cycles`, `cache-references`, `cache-misses` (LLC), `stalled-cycles-frontend`, `stalled-cycles-backend`, `L1-icache-prefetches`, `L1-icache-prefetch-misses`, `dTLB-load-misses`, `iTLB-loads`. Among them, `dTLB-load-misses` can be replaced by the raw selector `0x15` (see below).

### Sampling

X100 implements Sscofpmf, and `cycles` / `instructions` use ordinary programmable counters instead of `mcycle` / `minstret`, so `perf record`, `perf top` and other sampling functions work for these two events as well. This is different from X60.

If the chip also carries cores of other models, the whole chip shares a single Device Tree, so the event table is still the X100 one and perf does not tell the event meanings apart by core. When accurate numbers are needed, it is recommended to pin the measured process to an X100 core with `taskset`; when counting across cores with `perf stat -A`, the results on non-X100 cores need to be treated separately.

## How to Use Raw Hardware Events

For those events that are supported on hardware but not have pre-defined names in Linux perf framework (called "raw hardware event"), we can use `-e` option with the following two ways to specify them:

- By `rNNN` encoding
- By name (Requires the SDK of this platform to have implemented the pmu-events json files)

### By `rNNN` encoding

`-e rNNN` can be used to specify a event by the selector defined in hardware, where `NNN` is a hexadecimal number (excluding `0x`).

For RISC-V platforms that support SBI PMU Extension, `NNN` is the selector written into the `mhpmevent` CSR itself:

```plain
  [63:48]   must be 0
  [47:0]    the corresponding mhpmevent selector
```

For example, to count the event whose selector is `0x15`, use `-e r15`.

> Do not write it as `r0400000000000008`, which encodes `PERF_TYPE_RAW` into the high bits. The event type is passed by the perf tool through `attr.type`, and `config` should hold nothing but the selector; when the high bits are not 0, newer kernels reject the event outright, while older ones silently keep only the low 48 bits.

Also, **not every selector can be used**: only the selectors allowed by the firmware in `riscv,raw-event-to-mhpmcounters` can be opened.

- X60 allows `0x1` to `0xff` (the indexes actually valid in hardware are `0x1` to `0xbd`).
- X100 allows the following 47: `01 02 05 06 07 08 09 0a 0b 0c 10 11 12 13 14 15 16 17 18 19 1a 1b 1e 1f 20 21 22 24 25 26 27 28 29 2b 2d 32 33 34 35 36 37 38 3a 3b 3c 3d 3f`.

The `dTLB-load-misses` mentioned above is such a case: the Device Tree of X100 defines no name mapping for it, but the selector `0x15` is allowed, so it can be counted with `-e r15`.

### By Name

perf allows vendors to add some json files to its source code, to define names for their specific raw hardware events. Then the users can specify events by name rather than `rNNN` encoding.

If implemented, the json files can be found in the Linux source code of the SDK in the directory `tools/perf/pmu-events/arch/riscv`. For example, for X60, there are:

```shell
user@host:~/linux/tools/perf/pmu-events/arch/riscv$ tree spacemit/x60
spacemit/x60
|-- branch.json
|-- cache.json
|-- instruction.json
`-- microarch.json
```

When **using the perf tool complied from this source code**, users can use the names defined in the json files instead of the `rNNN` encodings.

Take the following content in X60 `cache.json` as an example:

![X60 perf pmu-events cache.json](./static/perf-pmu-events-json-cache-l1d.png)

- `EventName` is the name can be used in perf `-e` option.
- `EventCode` corresponds to the HPM event code (usually described in the hardware user manual).

We can find these names in `perf list` (If the result of `perf list` is too long, we can only list the events related to the keyword, such as `perf list l1`):

![X60 perf list - L1D events](./static/perf-pmu-events-list-cache-l1d.png)

This name can be used directly in `-e` option. For example:

![perf pmu-events example](./static/perf-pmu-events-example.png)

If the current SDK does not provide json files for the platform, only `rNNN` encoding can be used.
