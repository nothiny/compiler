# Target: SpacemiT K3 A100 — QEMU functional development

This document describes the target for a compiler that lowers the Triton-style
operators in `ops/` to complete native operator executables. Development runs use
the pinned functional emulator; execution on the board is a later porting step.

Provenance labels:
- **FACT** is an observed environment result with its report cited.
- **DOCUMENTED** is a hardware property from a cited manual, not measured here.
- **POLICY** is this project's required compiler behavior.
- **UNKNOWN** remains unverified and must not be treated as a capability.

Knowledge profile: k3-a100
Acceptance scope: correctness_only
Required execution evidence: resources

## Project scope

**POLICY** Generated computation targets A100 cores only. Support 1/2/4/8 compute
workers, RVV vectorization and applicable real IME matrix paths. Current acceptance
is correctness only: no performance metrics, benchmark target or measured
performance round is required. The two inputs are this description and `ops/`.

**POLICY** Basic compiler optimizations remain implementation requirements:
CSE, DCE, constant folding/propagation, copy propagation, strength reduction and
LICM, applied under the source semantics and valid dependence/alias conditions.
Integrate them into the normal compilation pipeline and validate the enabled
pipeline against the original cases. Their implementation and rewrite checks
need no timing, speedup, depth ladder or additional completion gate.

## 1. Target identity

**DOCUMENTED** A100 implements RVV 1.0 with VLEN=1024. The documented IME tile
families include INT4 8x32x8, INT8 8x16x8 and FP16/BF16 8x8x8 with FP32 floating
accumulation. Exact operand, register, layout and control-state restrictions must
come from the sourced instruction specification, not these summary dimensions.
Sources are indexed in `docs/compiler-agent/TARGET_SUMMARY.md`; versions and
digests are in `docs/compiler-agent/target-material/manifest.json`. Read the
cited original through knowledge search before recording a Fact.

## 2. Compiler target boundary (the codegen contract)

```text
Triton operator + target description
  -> this compiler: semantics, dependency analysis, work partition, vector/matrix
     lowering, instruction selection, allocation, stages and program-level assembly
  -> declared assembler and linker + common native runtime/system libraries
  -> standalone native executable
  -> QEMU now; A100 board after porting
```

**POLICY** The compiler generates the complete single-operator execution program,
including entry/argument binding, worker range loops, computation, constants and
workspace descriptions. A precompiled C/C++ runtime may provide threads,
synchronization, memory and I/O; per-operator C wrappers are not required. Do not
replace this compiler's lowering with a generated high-level translation unit.

**POLICY** Python may compile and perform external preparation/comparison. Running
`./operator_exec` must neither start, embed nor call Python. Program iteration,
ID calculation, argument access and kernel calls all execute in native code.

## 3. Execution model

**POLICY** Parallelize one operator across native workers and vectorize within
each worker. Work may be repartitioned from the source grid when semantics permit.
A persistent pool receives native work ranges; reuse threads and workspaces across
calls. Cross-worker dependencies use explicit stages, synchronization and merges.
Validate coverage, tails, ownership, visibility and repeated execution at 1/2/4/8
workers. Representative multi-worker cases must distribute useful work, and
applicable matrix cases must execute real IME instructions.

## 4. Input and numeric contract

**POLICY** The prepared `ops/` corpus declares the operators, shapes, dtypes,
grids and independent comparisons. Read its own documentation and enumerate with
its harness. Preserve all supplied cases and comparison policies. Integer, index
and boolean outputs remain exact; floating transformations must remain within
each case's original tolerance. Never change the reference or tolerance to pass.

**FACT** Corpus origin and recorded case adaptation are in
`docs/compiler-agent/CORPUS_LOCK.json` and
`docs/compiler-agent/A100_CORPUS_DERIVATION.json`.

## 5. Toolchain and execution endpoints

**FACT** `a100_support/lock.json` and `a100_support/env.sh` locate the installed
cross GCC, assembler, linker, sysroot and jdsk-qemu 10.0.2. QEMU uses
`-cpu max,vlen=1024,elen=64,vext_spec=v1.0`. Actual tool versions and executed
instruction/worker probes are in `docs/compiler-agent/TOOLCHAIN_PROBES.json`.

**POLICY** QEMU executes the compiler's native target program. Compiled x86
Triton CPU is a separate question-validation service with independent references;
it never substitutes for candidate target execution. Its current full reference
report is `docs/compiler-agent/A100_REFERENCE_AUDIT.json`.

## 6. Validation hierarchy

**POLICY** First validate the prepared execution environment, then compile,
execute and compare actual generated operators over the complete input set.
Environment probes and x86 reference audits do not certify the compiler. Retain
source-bound multi-worker and matrix instruction evidence in the prepared current
regression. Do not require timing or speedup evidence to finish this project.

## 7. Unknowns and assumptions

**UNKNOWN** QEMU guest threads do not establish physical A100 core identities,
topology, affinity, cache behavior or timing. Discover and validate those on the
board during porting; do not guess them from the emulator configuration.

**UNKNOWN** The pinned emulator's BF16 IME format selection has not passed.
Preserve BF16 semantic coverage and record this instruction-path gap separately;
FP16 or ordinary vector success cannot prove BF16 IME execution.

The pack below is sourced reference material. Other-chip examples, earlier matrix
proposals and performance chapters do not expand this project's requirements.

## Target pack

<details>
<summary>自动维护的本地资料清单；来源、版本和摘要见知识包 manifest</summary>

- `docs/compiler-agent/target-material/sources/432da714bd719f3506e3fb28b39f1f35fa1a8f54702382d66e010ec92acb30f6/root_overview.md`
- `docs/compiler-agent/target-material/sources/432da714bd719f3506e3fb28b39f1f35fa1a8f54702382d66e010ec92acb30f6/root_overview.md.search.txt`
- `docs/compiler-agent/target-material/sources/69a7cd5b8836085506f53f1b02ad8aa624790eb23ca573ca584e226ee1246358/k3_ds.md`
- `docs/compiler-agent/target-material/sources/69a7cd5b8836085506f53f1b02ad8aa624790eb23ca573ca584e226ee1246358/k3_ds.md.search.txt`
- `docs/compiler-agent/target-material/sources/980d492c33935188f7977a79c8c7a269581abfed2e68b1a2ee8560a955b0943c/01_overview.md`
- `docs/compiler-agent/target-material/sources/980d492c33935188f7977a79c8c7a269581abfed2e68b1a2ee8560a955b0943c/01_overview.md.search.txt`
- `docs/compiler-agent/target-material/sources/4f7d0d5c4e77c7a0647e946a698656682ead8a9ae7fbc9fae6a83da37e625c6e/06_address_map.md`
- `docs/compiler-agent/target-material/sources/4f7d0d5c4e77c7a0647e946a698656682ead8a9ae7fbc9fae6a83da37e625c6e/06_address_map.md.search.txt`
- `docs/compiler-agent/target-material/sources/5d4c71fd428bb11411778b0628324cc794916d3241046f45f6c192022c80af57/07_interrupts.md`
- `docs/compiler-agent/target-material/sources/5d4c71fd428bb11411778b0628324cc794916d3241046f45f6c192022c80af57/07_interrupts.md.search.txt`
- `docs/compiler-agent/target-material/sources/ff2340c355516e190769949abbfe57d2121efbe72326b5fc65b166f6cd55d90d/08_cpu.md`
- `docs/compiler-agent/target-material/sources/ff2340c355516e190769949abbfe57d2121efbe72326b5fc65b166f6cd55d90d/08_cpu.md.search.txt`
- `docs/compiler-agent/target-material/sources/555a9e44f2b4ac508251fc459abd2f3356e21469e346a430295c0223af9c2007/09_memory_storage.md`
- `docs/compiler-agent/target-material/sources/555a9e44f2b4ac508251fc459abd2f3356e21469e346a430295c0223af9c2007/09_memory_storage.md.search.txt`
- `docs/compiler-agent/target-material/sources/e3c328de09ccec8594134bfa2d29c635b7cc78578dde2cfe28de169983b9ecb7/dma.md`
- `docs/compiler-agent/target-material/sources/e3c328de09ccec8594134bfa2d29c635b7cc78578dde2cfe28de169983b9ecb7/dma.md.search.txt`
- `docs/compiler-agent/target-material/sources/18ed67a57de04224793b95fab0299ba71445f1fc27dd3d0511528fd284cd232e/spinlock.md`
- `docs/compiler-agent/target-material/sources/18ed67a57de04224793b95fab0299ba71445f1fc27dd3d0511528fd284cd232e/spinlock.md.search.txt`
- `docs/compiler-agent/target-material/sources/dc037f1ccf98cb7650005c4af256b0b1ce2cc8fc2580ba5faf4079cf133ad1d7/power_management.md`
- `docs/compiler-agent/target-material/sources/dc037f1ccf98cb7650005c4af256b0b1ce2cc8fc2580ba5faf4079cf133ad1d7/power_management.md.search.txt`
- `docs/compiler-agent/target-material/sources/d97576dbc399e781c35136e5fed56e15a75b34985d6fac9498ca4e225b2aea49/17_clock_reset.md`
- `docs/compiler-agent/target-material/sources/d97576dbc399e781c35136e5fed56e15a75b34985d6fac9498ca4e225b2aea49/17_clock_reset.md.search.txt`
- `docs/compiler-agent/target-material/sources/a6906d24be9df2d032e7c44206c381379d48cebe8b1d2bdbbd5172789a25ee8b/root_overview.md`
- `docs/compiler-agent/target-material/sources/a6906d24be9df2d032e7c44206c381379d48cebe8b1d2bdbbd5172789a25ee8b/root_overview.md.search.txt`
- `docs/compiler-agent/target-material/sources/d18ac403d0440ee8554842d7ebe9234c04224682329f5be20e0bc720d3af98fc/k3_sdk_user_guide.md`
- `docs/compiler-agent/target-material/sources/d18ac403d0440ee8554842d7ebe9234c04224682329f5be20e0bc720d3af98fc/k3_sdk_user_guide.md.search.txt`
- `docs/compiler-agent/target-material/sources/bd69e01a6280ae5ab4493ea82b0e819fb34f093da43c264fc3be3c6291a8c6c8/ime_extension.md`
- `docs/compiler-agent/target-material/sources/bd69e01a6280ae5ab4493ea82b0e819fb34f093da43c264fc3be3c6291a8c6c8/ime_extension.md.search.txt`
- `docs/compiler-agent/target-material/sources/462bf27aed1712f9ca43fee5cb6302de444e4e1c66f513a08be5a8bd62b445a1/instruction.md`
- `docs/compiler-agent/target-material/sources/462bf27aed1712f9ca43fee5cb6302de444e4e1c66f513a08be5a8bd62b445a1/instruction.md.search.txt`
- `docs/compiler-agent/target-material/sources/83ddde6d173d633a2b89bad966f7ec23ae7ab4699185cf85989521a79c03d066/concept.md`
- `docs/compiler-agent/target-material/sources/83ddde6d173d633a2b89bad966f7ec23ae7ab4699185cf85989521a79c03d066/concept.md.search.txt`
- `docs/compiler-agent/target-material/sources/f97e5fa486885796bd4c24b204159f6c959cfe87015e5516c87d78ed9fc201d7/triton.md`
- `docs/compiler-agent/target-material/sources/f97e5fa486885796bd4c24b204159f6c959cfe87015e5516c87d78ed9fc201d7/triton.md.search.txt`
- `docs/compiler-agent/target-material/sources/95f02e5ac780f3e3746f08cca80431e7921eed3f56a83bf4b27d13835d37fbed/onnxruntime.md`
- `docs/compiler-agent/target-material/sources/95f02e5ac780f3e3746f08cca80431e7921eed3f56a83bf4b27d13835d37fbed/onnxruntime.md.search.txt`
- `docs/compiler-agent/target-material/sources/73b1bbf426167572923c4c1c7ac5a6caef5b6146f2071f10c6e5d77f66e3de2d/onnxruntime_ep_faq.md`
- `docs/compiler-agent/target-material/sources/73b1bbf426167572923c4c1c7ac5a6caef5b6146f2071f10c6e5d77f66e3de2d/onnxruntime_ep_faq.md.search.txt`
- `docs/compiler-agent/target-material/sources/160a000a6d680a485400bcd5d41461504f1f9ecd16081bce885e94b4f714540b/llama.cpp.md`
- `docs/compiler-agent/target-material/sources/160a000a6d680a485400bcd5d41461504f1f9ecd16081bce885e94b4f714540b/llama.cpp.md.search.txt`
- `docs/compiler-agent/target-material/sources/22375bca9186501ada02cc4bd89cac6820aad719ffaddf373aa277c839fc67fb/math_library.md`
- `docs/compiler-agent/target-material/sources/22375bca9186501ada02cc4bd89cac6820aad719ffaddf373aa277c839fc67fb/math_library.md.search.txt`
- `docs/compiler-agent/target-material/sources/efb5d87ac66581c12a931698b95db2ae840a57110cf23e429142fca07662e189/ime_extension.md`
- `docs/compiler-agent/target-material/sources/efb5d87ac66581c12a931698b95db2ae840a57110cf23e429142fca07662e189/ime_extension.md.search.txt`
- `docs/compiler-agent/target-material/sources/600d07cca6c35f0e81c707bb13ba35492acc3b7a9eabc9c096e32014dbeb6305/README.md`
- `docs/compiler-agent/target-material/sources/600d07cca6c35f0e81c707bb13ba35492acc3b7a9eabc9c096e32014dbeb6305/README.md.search.txt`
- `docs/compiler-agent/target-material/sources/03c1b05824500546d8d63671bc85b2e24b6cf23aee4a4027c9abe291e504e28c/perf.md`
- `docs/compiler-agent/target-material/sources/03c1b05824500546d8d63671bc85b2e24b6cf23aee4a4027c9abe291e504e28c/perf.md.search.txt`
- `docs/compiler-agent/target-material/sources/a40604be99c1d301eec85b726613b54d625453399d237e7cdaf38ef7de55d52f/k3_block_diagram.png`
- `docs/compiler-agent/target-material/sources/d9124b947c314d54b99c2fdef03e244ff543d18db145238d49fff54e4376543c/x100_block_diagram.png`
- `docs/compiler-agent/target-material/sources/d07d1164890ac99841f4300a2651f7d9416bb1462bebce8e581048bdb723ba5e/a100_block_diagram.png`
- `docs/compiler-agent/target-material/sources/1d608a7cf912ac591d93409457b1b188a2e6e76f60d4839136efaf8a55d71b8f/rt24_block_diagram.png`
- `docs/compiler-agent/target-material/sources/523f54f20c34eeaebaf05a45e370422e27ef8400f13d097709feddd3ca528556/debug_block_diagram.png`
- `docs/compiler-agent/target-material/sources/9fb9dc6130f4cd82ebb34cf534d945debeedaa801e821566db16d40a60d9560b/trace_block_diagram.png`
- `docs/compiler-agent/target-material/sources/5206ef71463c4ed51af9e366ddde19028b0b28bde60f4d069c842e8ba3a2a5f6/mipi_block_diagram.png`
- `docs/compiler-agent/target-material/sources/f790e8f70ff2ff298c9d21b5679376ae5832e7999dd2ef5994c1f80762b1da46/disp_input_addr.png`
- `docs/compiler-agent/target-material/sources/1bcf566d9226caf81cec9c52b335e0ea4c6d94d1bc0e89449e711c926d09a44e/usb_block_diagram.png`
- `docs/compiler-agent/target-material/sources/1142c53f56ccd837008a1161f585e92dbc8fd75c6a92c0fb6ed4217338fb899f/i2c_block_diagram.png`
- `docs/compiler-agent/target-material/sources/7dece30d6ba35caee0cd4ee4c95cc5343c74b4d0f8da29708a3882666971866f/espi_block_diagram.png`
- `docs/compiler-agent/target-material/sources/c19e5b175f6b1b3930ccadbceecccedc7295b812d6c9124ea2967fdbd16fa9cc/dma_block_diagram.png`
- `docs/compiler-agent/target-material/sources/2e69b18aff414f3d0ee2ed3ce3ca849fd3cf0cd946570460b2076d5747267bb8/mailbox_block_diagram.png`
- `docs/compiler-agent/target-material/sources/5f6bc560ae58ba69d95e2e856e159026ff946a8bcf2da6b1d9f158f038e2922e/package1.png`
- `docs/compiler-agent/target-material/sources/d32c51b011413d40ce729d30069a15af3ac5be76af5f616cf1fec08924835ee4/package2.png`
- `docs/compiler-agent/target-material/sources/88e745335bef439bc8f7907033129b46293f0915c7554be5c731a79142ba2ea7/k3_partno.png`
- `docs/compiler-agent/target-material/sources/b0e4e8a2b0fd834751e10f5fe83d27bbae379eb7e0b733926b92f9128ca12db7/k3_pinmap.png`
- `docs/compiler-agent/target-material/sources/4ff2b7cb24b7f57b1ed4c4ff2a36e8b41316e287300ae64dcfb5fb0e0ee1e023/k3_pinmap_a-y_1-20.png`
- `docs/compiler-agent/target-material/sources/242dea3dfeb5224c57db03c02bbbf184449b545347eec881020641a5b3b71aca/k3_pinmap_a-y_21-40.png`
- `docs/compiler-agent/target-material/sources/f6b873a6399c1f48bddc71b4042472cd561acbed9907b18b4080d108d742d006/k3_pinmap_aa-ay_1-20.png`
- `docs/compiler-agent/target-material/sources/8594e33106b1a444b5b70062b24921856dd2a37d72f715806d516cf988d56811/k3_pinmap_aa-ay_21-40.png`
- `docs/compiler-agent/target-material/sources/e0824223b2514ab942cea301ac36929a2cb4e0bab7a6dd7bd25947aa7781f264/k3_block_diagram.png`
- `docs/compiler-agent/target-material/sources/8890a8162b71945d4197cd74a44c27e56c3df7590d88580ba3cc84e3b6e776ab/x100_block_diagram.png`
- `docs/compiler-agent/target-material/sources/98a28f614703b678187c7646147975b13def77bbe20239e269278a199380ac67/a100_block_diagram.png`
- `docs/compiler-agent/target-material/sources/c87c319e8e1500f51ad1da76287c1b3ea01cdce9551bbc338ab98720ba03add7/rt24_block_diagram.png`
- `docs/compiler-agent/target-material/sources/988daeb1a1f10dac51bdf080f9788ee7c1b0dc043c4c4fc6d25823fd16bf6674/debug_block_diagram.png`
- `docs/compiler-agent/target-material/sources/0af5cd98c005ebd850191b50253dc87d2d8214dadf7f9af53892e7a88bfebf92/trace_block_diagram.png`
- `docs/compiler-agent/target-material/sources/9f1908d0dea88c5501c7cc381ec81d4dcfd3214599e53b0906af0a533d92f675/memory01.png`
- `docs/compiler-agent/target-material/sources/62038bfdda74e414ff9594d15146ee98af71720e123e364bc192142611a3bd5c/k3_lpddr.png`
- `docs/compiler-agent/target-material/sources/8ec1774c95a3417cb8a6f6ae2be49c2049f2eb81873a9743ca7f647c87a70c22/k3_qspi00.png`
- `docs/compiler-agent/target-material/sources/7386e6c74a4b511ed30c912d9ebed34de10e0a38172681bf09f4a9631d848f0d/k3_qspi01.png`
- `docs/compiler-agent/target-material/sources/26d477e2cea23e892320327de504ea30bb7b70762eba73fe31d213df9b287b82/k3-emmc-bd.png`
- `docs/compiler-agent/target-material/sources/773fb210f5f54037d3d33f5b7f1768affa3a9d0f66746f65da43bac503c5459c/k3-emmc.png`
- `docs/compiler-agent/target-material/sources/85f86fae077ae76deb01262266491bcc314836f70c7d94e29b765428fa8fbfad/ufs_bd.png`
- `docs/compiler-agent/target-material/sources/542b947f7f8291375bee913899c4cac9541e97408cf960eda2e5005cda2d2b89/ufs00.png`
- `docs/compiler-agent/target-material/sources/3d3a14307ff54d733bd1d7e93f77dfc488af3ab73d5c9910a41bc3944c8fed94/ufs01.png`
- `docs/compiler-agent/target-material/sources/84e4bff4442b845e5194dec5d79d68a95727201336fedb5b57b9cb86aae2f3b8/dma_block_diagram.png`
- `docs/compiler-agent/target-material/sources/bd0c7f5e741c03beaf7b71b255b96125429401254775cf6cad1544b02822254e/dma_operations.png`
- `docs/compiler-agent/target-material/sources/54313589ac0fea62e9e4b8210b76abff629d25015c4ad53778d74fbbfcc70129/dma_operations_1.png`
- `docs/compiler-agent/target-material/sources/be14615f38d02d00c3b3a22662fb51480f31296f29e35062ad92465c842a0e0d/dma_operations_2.png`
- `docs/compiler-agent/target-material/sources/c03276c6b403e8600c961964f0a9b91321830211ac779fd343fbcac1f39a0170/spinlock.png`
- `docs/compiler-agent/target-material/sources/59b1205a05a837928cf635fa5b0041720db7e24c3b401bbeeb8957e1c32886e0/spinlock01.png`
- `docs/compiler-agent/target-material/sources/c380ee1efbbf9b0046a5063312989d77d5a850a813711c9d8c728210c8860ddf/spinlock02.png`
- `docs/compiler-agent/target-material/sources/4ff7a37f890480b817c0ee452457327b2c485f63db66180e5e9dbdd43c98cf2d/k3_clock_tree.png`
- `docs/compiler-agent/target-material/sources/16b032a698a68d68ee82495ce785fcfed740170c87312482be56cadc0d18551f/k3_block_diagram.png`
- `docs/compiler-agent/target-material/sources/3e053740741d138c326e5b72c9cb7b8c132d8c4dc05d7e8935dc0261f8a3ff24/fig0vlen256.png`
- `docs/compiler-agent/target-material/sources/672840b63b7a063e2fc0445ab68534124c156ec3a4a1ac1cf918d9f34e8f0780/fig1ime-tile-lmul_2_4.png`
- `docs/compiler-agent/target-material/sources/d11cf0567dbb0557c19d9e65385906f019be12b418cda48f5a79d6105c8931ba/fig2tilelayout.png`
- `docs/compiler-agent/target-material/sources/ed0482dfd0bfb7e089357ce2f7f44000832d27006445fab50fbd029c7e525959/fig3vmadot.png`
- `docs/compiler-agent/target-material/sources/4c843856a5e52c6d201ddf894a74c48107caa376c99031d83e14a0bfe7f58aa7/fig4vmadotslide.png`
- `docs/compiler-agent/target-material/sources/033accd59793443de4f96ea9bcf113d789b8992e79007c41a8cff7e42d4128a8/fig5vmadotsp.png`
- `docs/compiler-agent/target-material/sources/0680625b8dad0a5ddc9ee5a65528450fc59495a8cd853998a4cb9e28f56b9388/fig6vmadothp.png`
- `docs/compiler-agent/target-material/sources/182e26f825e9c87d565a3fce0e9dd52adb79c3a35db1f5f7c7c24f181d92d603/fig7fwmadot.png`
- `docs/compiler-agent/target-material/sources/631bc3d344cf13cde99f377d41a9dae2dbaee3251a8cb110b865c84c1c66ddb7/fig8fwmadotslide.png`
- `docs/compiler-agent/target-material/sources/8c7af37914f03b87e4a1cc81c675e7dd40d46a590fe2789123eb59c9607e0d87/fig9packunpack.jpg`
- `docs/compiler-agent/target-material/sources/c6f7cac17c18ce122d3122423ba8cfdf01134ff555e694eaa0ef38f3202a8ef3/fig10packexample.jpg`
- `docs/compiler-agent/target-material/sources/83cea5b974db592d03cc48944bf7ed9fbbdd86ddd85d6abdc78812007b81459f/matrix_inst.jpg`
- `docs/compiler-agent/target-material/sources/18f6aa9139edb09a66db9b528f7981b5af3f510db2caea018da9e9d1d7c2bdef/architect.webp`
- `docs/compiler-agent/target-material/sources/0ffe4114ad3a8e903090eb7747b5d8d2886c10c38dc027da56a73b5c19d5b1d5/llama-cpp-icon.png`
- `docs/compiler-agent/target-material/sources/9e2bb7d239a200e1e5d3fa07f0f1a0ddcfa9fb194a53f9c06390d1f4d7b98f85/llama-bench.png`
- `docs/compiler-agent/target-material/sources/864eac4429da80db4ba7a37bf8fcff768f2789624f45d27742b5becf712dd6ed/llama-cli.png`
- `docs/compiler-agent/target-material/sources/4dc088f17e275d6bb96ed3837fec82b9c9d7edad49360b433dea7e8db5e107f2/llama-server-api.png`
- `docs/compiler-agent/target-material/sources/5a877fb77c41c1991cc991385cbdd66d237c7007e87d7f3ecc01cdacd1049b0b/llama-server-chrome.png`
- `docs/compiler-agent/target-material/sources/4ffff28d0e175c0e461ed3b4c08eb9a9897cbc4a91c8a9cb6521c0ba92809ac7/vlm-folder-structure.png`
- `docs/compiler-agent/target-material/sources/87efa7d3dd155aa74575f4bace4e64b11765a953df6cae4336ded8ee1f29f95e/qwen35-0.8b-folder-structure.png`
- `docs/compiler-agent/target-material/sources/0d88dac1ef60dd076493644ea51a2cc5755389372ac4dfc6a06941f41d73375a/vlm-ready.png`
- `docs/compiler-agent/target-material/sources/2e98f3948262a47f957f74045e358d180ff39f8cd45f8189829c78f3c8e71559/vlm-chrome.png`
- `docs/compiler-agent/target-material/sources/b06d7bacc5053a064beca080fde28b3b2559c7958609faf10e9a80fde03db95e/vlm-performance.png`
- `docs/compiler-agent/target-material/sources/3e0eff71c275af7984b43577e168d548ef856acdfdae5d964ad8d2dbe73fa832/vlm-30b-a3b-chrome.png`
- `docs/compiler-agent/target-material/sources/43ea00c0740933cdfa9831a545685bab2d4e39cda912928a6af8aaadbab2625f/vlm-30b-a3b-performance.png`
- `docs/compiler-agent/target-material/sources/2609e44c2513859b63f18ce426342b8683c45496b0241577e08638f2b9c86880/tcm-busy-8.png`
- `docs/compiler-agent/target-material/sources/a6c81417c780fa70416eacbfdc96fe9040723bfd5280e7fa5e21a04e663f80c8/tcm-fail.png`
- `docs/compiler-agent/target-material/sources/d320fd0485a3f5139b419aa1a5fbd8e1b6bb5bbfa75c413d6535d9013051d4d2/tcm-free-8.png`
- `docs/compiler-agent/target-material/sources/377c997a3c8950bc9e15de8fdd54384a53fd44fa6e01e76afc22f858b050b16f/tcm-busy-4.png`
- `docs/compiler-agent/target-material/sources/ceaeef27ebfb07143508230751c381c444ae2826237b9107dc3f2c7744af7a06/fig0vlen256.png`
- `docs/compiler-agent/target-material/sources/8fcc855091460cc33da2b2c2e44691e92f30eb6ee9c2e46a789004a6d44095e1/fig1ime-tile-lmul_2_4.png`
- `docs/compiler-agent/target-material/sources/72e21872a262f4b054a84465ad7f84704bf67fe6a46e07337ea6177768cef62c/fig2tilelayout.png`
- `docs/compiler-agent/target-material/sources/63e8af688500797c8df0a4f4e29a3bf6586c2b03135ee341e191c3ad5d990da0/fig3vmadot.png`
- `docs/compiler-agent/target-material/sources/cab497b6442aef6cfa12c45bdaafb395eec5e79ede4b1494561658027b950189/fig4vmadotslide.png`
- `docs/compiler-agent/target-material/sources/7e9db671fb6a0dc2e49ddfbbf3c33f2c889261713a3cf3ea8ca99ee041ec7dee/fig5vmadotsp.png`
- `docs/compiler-agent/target-material/sources/4b15fabdd3a470754335e02c47d5391bf55ced4e8f9c07d057501e272dbdbaab/fig6vmadothp.png`
- `docs/compiler-agent/target-material/sources/a4e593d6239e5b0ddb488c1fb17ed89a51c5a7c3e8f3f407d84212820401784b/fig7fwmadot.png`
- `docs/compiler-agent/target-material/sources/29b746d7ff36bedf49265d573cfcecd2d94ef846f84feae76131d7002df5c350/fig8fwmadotslide.png`
- `docs/compiler-agent/target-material/sources/3817cdd1eea1c3e813683fbb967aa5a2b9d7ee7e13ebe39a69069291bfea8d4a/fig9packunpack.jpg`
- `docs/compiler-agent/target-material/sources/25e4a56582b45ed5dc2acaf6072c10e7e1105288bcde487122d206c149810490/fig10packexample.jpg`
- `docs/compiler-agent/target-material/sources/685c391bd3a66ce9ce9ccc754b9aa4b0d4897de99f692795ed0097b1b05b999d/perf-framework-riscv.png`
- `docs/compiler-agent/target-material/sources/0d1c41f462f102e7c9b7627d5d48797e99505793be7bbb46e9a26f1cf75a2395/perf-record-error-no-samples.png`
- `docs/compiler-agent/target-material/sources/fd166a9b7c13318e82808571e1f3c530fcb85f9690d0a00b3028f6b9f7565b6c/perf-framework-sscofpmf-cycle-instret.png`
- `docs/compiler-agent/target-material/sources/4371da015686a00eaeb783477f0f332dff9c51fc2a8aba042a70b16235279c61/perf-record-branches.png`
- `docs/compiler-agent/target-material/sources/97b75e34d11a3b02ac2b61ebcc51769eeae0af476e078081b40f099fed973b42/perf-pmu-events-json-cache-l1d.png`
- `docs/compiler-agent/target-material/sources/185a1830d76a3f6fffb0efb81350a3454c7216a6934bff82b728a2070b9fa276/perf-pmu-events-list-cache-l1d.png`
- `docs/compiler-agent/target-material/sources/fedfedba87a4c507b9428810019be365a65c9e8242a94f4d882929e93376cdcb/perf-pmu-events-example.png`
- `docs/compiler-agent/target-material/sources/9564d4ba5ed9a64d71c0c7e5bf0c8f7d74ed717fd0aa71265328f8c1eaea8c91/K3_architecture_preview.pdf`
- `docs/compiler-agent/target-material/sources/9564d4ba5ed9a64d71c0c7e5bf0c8f7d74ed717fd0aa71265328f8c1eaea8c91/K3_architecture_preview.pdf.search.txt`
- `docs/compiler-agent/target-material/sources/18ecc1af73309ba3af0e9205a61f9fa80ad55735855406ab4cd1aa2d2e9ce69a/K3_brief_zh.pdf`
- `docs/compiler-agent/target-material/sources/18ecc1af73309ba3af0e9205a61f9fa80ad55735855406ab4cd1aa2d2e9ce69a/K3_brief_zh.pdf.search.txt`
- `docs/compiler-agent/target-material/sources/49175158ccc9a8b028a740ab45c6ea03dc2560ba8c6739bd298df1dc01452f63/A100_project_summary.md`
- `docs/compiler-agent/target-material/sources/49175158ccc9a8b028a740ab45c6ea03dc2560ba8c6739bd298df1dc01452f63/A100_project_summary.md.search.txt`

</details>
