<script>
  import WrittenUnits from "$lib/WrittenUnits.svelte";
</script>

<h2>Architecture</h2>

<p lang="en">Each writing system using Mongolian script and the unified writing system formed by integrating them have the same architecture of text representation and text shaping. The text representation and text shaping rules contained in the individual writing systems and the integrated writing system are the concrete realization of this common architecture. This chapter describes this common architecture, and subsequent chapters describe the specific rules of each writing system in detail.</p>
<p lang="zh">使用蒙古文字的各个书写系统，以及综合这些书写系统所形成的统一的书写系统，均具有相同的文本表记与文本成形架构。每种书写系统及其综合系统所包含的文本表记与文本成形规则，都是该共同架构的具体实现。本章将介绍这一共同架构，后续章节将详细说明各个书写系统的具体规则。</p>

<h3>Data files and the standard toolchain</h3>

<p lang="en">The text shaping data for Mongolian script are in the form of machine-readable files that provide the character attribute information, text shaping rules, font generation program, and font testing program for Mongolian script.</p>
<p lang="zh">蒙古文字的文本成形数据以机器可读的文件形式，提供蒙古文字的字符属性信息、文本成形规则信息、字库生成程序和字库测试程序等内容。</p>

<p lang="en">The character attribute information and text shaping rules of Mongolian script provide the correspondence between Mongolian characters and variants in each writing system, and the correspondence between Mongolian character strings and glyph sequences. The font generation program is capable of completing and generating a usable font by providing the basic design file, the correspondence information between glyph images and variants, and the setting information. The font testing program can test how the font supports each writing system by providing the font file and the correspondence between glyph images and variants.</p>
<p lang="zh">蒙古文字的字符属性信息和文本成形规则信息，详细描述了各书写系统中蒙古文字字符与字形的对应关系，以及蒙古文字字符串与字形序列的对应关系。字库生成程序在提供基础字库文件、字形图像与字形的对应关系信息和设定信息的情况下，能够增补并生成可用的字库。字库测试程序则在提供字库文件和字形图像与字形对应关系信息的情况下，能够测试字库对各书写系统的文本成形规则的支持情况。</p>

<h3>Character set</h3>

<p lang="en">The characters included in each writing system of the Mongolian script can be categorized into Mongolian-specific characters and characters shared with other scripts.</p>
<p lang="zh">蒙古文字的各书写系统所包含的字符可分为特有字符和共用字符。</p>

<table>
  <tbody>
    <tr>
      <th>Script</th>
      <th>Type of characters</th>
      <th>Character examples</th>
      <th>Note</th>
    </tr>
    <tr>
      <td rowspan="4">General</td>
      <td>Space</td>
      <td>space</td>
    </tr>
    <tr>
      <td>Punctuation</td>
      <td>middle dot, …</td>
    </tr>
    <tr>
      <td>Format controls</td>
      <td>ZWJ, ZWNJ, …</td>
      <td>participate in shaping</td>
    </tr>
    <tr>
      <td>Digits</td>
      <td>digit one, …</td>
    </tr>
    <tr>
      <td rowspan="4">Mongolian</td>
      <td>Punctuation</td>
      <td>birga, …</td>
      <td>less used now</td>
    </tr>
    <tr>
      <td>Format controls</td>
      <td>nirugu, FVS, …</td>
      <td>participate in shaping</td>
    </tr>
    <tr>
      <td>Digits</td>
      <td>digit one, …</td>
      <td>less used now</td>
    </tr>
    <tr>
      <td>Phonetic letters</td>
      <td>letter <i>a</i>, …</td>
      <td>participate in shaping</td>
    </tr>
    <tr>
      <td>CJK</td>
      <td>Punctuation</td>
      <td>question mark, …</td>
    </tr>
  </tbody>
</table>

<h4>Phonetic letters and written units</h4>

<p lang="en">
  Due to the introduction of <i>matres lectionis</i>, for the writing systems using Mongolian script, both vowels and consonants of the written language correspond to the actual texts, and both are similar in behavior and equal in status. Therefore, although the original writing system was abjad, each writing system using Mongolian script has the characteristics of an alphabet.
</p>
<p lang="zh">
  由于 <i>matres lectionis</i> 的引入，对于使用蒙古文字的书写系统来说，其记录的书面语中的元音音位和辅音音位均对应于文本元素，并且这两种文本元素的行为相似、地位均等。因此，即使原有的书写系统属于 abjad，使用蒙古文字的各个书写系统也因此带有了 alphabet 的特征。
</p>

<p lang="en">
  These writing systems, with the characteristics of both abjad and alphabet, result in two ways of analyzing and encoding the Mongolian script. One is to determine the graphemes used by each writing system by chronologically comparing Mongolian script with Old Uyghur script and Old Turkic script, and to identify each grapheme as a character; the model formed by this method is called the <em>graphetic model</em>, and the basic unit in this model is called the <em>written unit</em>. The other is to analyze the phonemes of the written language recorded by the writing system, to group together the glyphs that record the same phoneme, and to identify each phoneme as a character; the model formed by this method is called a <em>phonetic model</em>, and the basic unit in the model is called the <em>phonetic letter</em>.
</p>
<p lang="zh">
  这些兼具 abjad 和 alphabet 特性的书写系统，产生了两种分析与编码蒙古文字的方式。一种通过将蒙古文字与回鹘文字、突厥文字等进行历时比较，确定各书写系统使用的形位，并将各个形位确定为字符，这种方法形成的模型称为<b>形位模型</b>，该模型中的基本单位称为<b>书写单位</b>。另一种通过分析书写系统所记录的书面语音位，归纳记录同一音位的字形，并将各个音位确立为字符，这种方法形成的模型称为<b>音位模型</b>，该模型中的基本单位称为<b>音位字母</b>。
</p>

<p lang="en">
  The specification used in this manual is based on the phonemic model, in which the characters correspond to the phonemes of the written language as recorded in the writing systems, with some compromises to maintain relative stability with the existing system. For example, the final <WrittenUnits>Ï</WrittenUnits> in Manchu records the phoneme /ɹ̩/, is the same as the phonetic letter <i>ï</i>, but because it corresponds to ⟨i⟩ rather than ⟨y⟩ in the Möllendorff transcription, it is treated as corresponding to the phonetic letter <i>i</i>
  rather than <i>ï</i>. This analysis is inherited in this specification.
</p>
<p lang="zh">
  本规范基于音位模型，其中各个蒙古文字的字符对应于其书写系统所记录的书面语音位，但也出于保持现有系统的相对稳定有所取舍。例如，圈点满文中前连形 Ï 所记录的书面语音位为 /ɹ̩/，虽与音位字母 <i>ï</i>
  相同，但由于穆麟德转写中该形位对应于 ⟨i⟩ 而非 ⟨y⟩，该形位被视作对应于音位字母
  <i>i</i>
  而非 <i>ï</i>。这一分析在本规范中得到继承。
</p>

<p lang="en">
  <b>Multi-to-one and one-to-multi confusion.</b>
  Since the writing units and the phonemes do not have a one-to-one correspondence, the phenomenon of the same phoneme corresponding to more than one written unit and the same written unit corresponding to more than one phoneme may occur. For example, in Hudum, the phonemic letter <i>n</i> is usually written as
  <WrittenUnits>N</WrittenUnits> when it appears as an onset and as <WrittenUnits>A</WrittenUnits> when it appears as a coda (except for loanwords such as <WrittenUnits>SWK2OIND</WrittenUnits>); and the grapheme sequence <WrittenUnits>AORDU</WrittenUnits> may correspond to <i>ordo</i>
  “palace”, <i>urtu</i> “long”, and <i>urdu</i> “south”.
</p>
