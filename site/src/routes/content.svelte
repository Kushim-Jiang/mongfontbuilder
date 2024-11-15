<script>
  import Chapter1 from "./chapter1.svelte";
  import Chapter2 from "./chapter2.svelte";
  import Reference from "./reference.svelte";
</script>

<h3><i>Summary</i></h3>
<p>
  <i
    >This document provides a system of text representation and text shaping
    rules for Mongolian script. For text representation, this document lists the
    characters and their variants for letters and marks used in each writing
    system; for text shaping, this document provides hierarchical shaping rules,
    detailing the behavior of each shaping step and the conditions for the
    presentation of each variant.</i
  >
</p>
<h3><i>Status</i></h3>
<p>
  <i
    >This document is a <b>Unicode Technical Note</b>. Sole responsibility for
    its contents rests with the author. Publication does not imply any
    endorsement by the Unicode Consortium.</i
  >
</p>

<p>
  For information on Unicode Technical Notes including criteria for acceptance,
  see
  <a href="https://www.unicode.org/notes/">https://www.unicode.org/notes/</a>.
</p>

<!-- Contents -->

<h3><i>Contents</i></h3>
<ol>
  <li>
    <a href="#Introduction">Introduction</a>
  </li>
  <li>
    <a href="#Architecture">Architecture</a>
  </li>
  <ol>
    <li>
      <a href="#Data files and the standard toolchain"
        >Data files and the standard toolchain</a
      >
    </li>
  </ol>
  <li>
    <a href="#References">References</a>
  </li>
</ol>

<!-- Introduction -->

<Chapter1 />

<Chapter2 />

<Reference />
