<script>
  let { children } = $props();
</script>

<span>{@render children()}</span>

<style>
  span {
    font-variant-caps: all-small-caps;
    background-color: beige;
  }
</style>
