<script lang="ts">
  interface Props {
    written: string;
  }

  let { written }: Props = $props();
</script>

<span>{written}</span>

<style>
  span {
    font-variant-caps: all-small-caps;
    background-color: linen;
  }
</style>
