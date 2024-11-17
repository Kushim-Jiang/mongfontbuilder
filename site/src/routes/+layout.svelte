<script>
  const version = 4;

  const base = "https://www.unicode.org/notes/tn57/";
  const thisURL = new URL(`tn57-${version}.html`, base);
  const previousURL = new URL(`tn57-${version - 1}.html`, base);
</script>

<header>
  <hgroup>
    <p>Unicode Technical Note #57</p>
    <h1>Encoding and Shaping of the Mongolian Script</h1>
  </hgroup>

  <dl>
    <dt>Version</dt>
    <dd>{version}</dd>

    <dt>Authors</dt>
    <dd>Kushim Jiang</dd>

    <dt>Date</dt>
    <dd>{new Date().toISOString().split("T", 1)[0]}</dd>

    <dt>This Version</dt>
    <dd><a href={thisURL.href}>{thisURL}</a></dd>

    <dt>Previous Version</dt>
    <dd><a href={previousURL.href}>{previousURL}</a></dd>

    <dt>Latest Version</dt>
    <dd><a href={base}>{base}</a></dd>
  </dl>
</header>

<h2>Summary</h2>

<p>This document provides a system of text representation and text shaping rules for Mongolian script. For text representation, this document lists the characters and their variants for letters and marks used in each writing system; for text shaping, this document provides hierarchical shaping rules, detailing the behavior of each shaping step and the conditions for the presentation of each variant.</p>

<h2>Status</h2>

<p>This document is a <b>Unicode Technical Note</b>. Sole responsibility for its contents rests with the author. Publication does not imply any endorsement by the Unicode Consortium.</p>

<p>For information on Unicode Technical Notes including criteria for acceptance, see <a href="https://www.unicode.org/notes/">https://www.unicode.org/notes/</a>.</p>

<slot />

<footer>
  <p>Copyright © 2024 Kushim Jiang and Unicode, Inc. All Rights Reserved. The Unicode Consortium and Kushim Jiang make no expressed or implied warranty of any kind, and assume no liability for errors or omissions. No liability is assumed for incidental and consequential damages in connection with or arising out of the use of the information or programs contained or accompanying this technical note. The Unicode <a href="https://www.unicode.org/copyright.html">Terms of Use</a> apply.</p>

  <p>Unicode and the Unicode Logo are registered trademarks of Unicode, Inc. in the United States and other countries.</p>
</footer>

<style>
  :global {
    html {
      font-size: 18px;
      line-height: 1.25;
      font-family: ui-sans-serif, sans-serif;
      max-width: 50em;
    }
  }
</style>
