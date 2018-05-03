<template>
  <div class="hello">
    <p>{{msg}}</p>
    <p>{{$route.params.username}}</p>
  </div>
</template>

<script>
  export default {
    name: 'Hi1',
    data() {
        return {
            msg: 'Hi I am Clark1!'
        }
    }
  }
</script>

<style scoped>

</style>
