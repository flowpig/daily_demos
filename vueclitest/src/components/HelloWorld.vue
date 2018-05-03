<template>
  <div class="hello">
    <h2>{{msg}}</h2>
    <ul>
      <li>
        <router-link to="/">首页</router-link>
      </li>
      <li>
        <router-link to="/hi">Hi页面</router-link>
      </li>
      <li>
        <router-link :to="{name:'hi1',params:{username:'jspang'}}">Hi1页面</router-link>
      </li>
      <li>
        <router-link to="/hi/hi2">Hi2页面</router-link>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  data () {
    return {
      msg: 'Welcome to Your Vue.js App'
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
</style>
