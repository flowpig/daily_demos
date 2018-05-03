<template>
  <div class="hello">
    <p>{{msg}}</p>
    <router-view></router-view>
  </div>
</template>

<script>
  export default {
    name: 'Hi',
    data() {
        return {
            msg: 'Hi I am Clark!'
        }
    }
  }
</script>

<style scoped>

</style>
