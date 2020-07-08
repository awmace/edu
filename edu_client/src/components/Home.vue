<template>
    <div>
        <Top></Top>
        <Mid></Mid>
        <Bot></Bot>
    </div>
</template>

<script>
    import Top from "./cpdd/Top";
    import Mid from "./cpdd/Mid";
    import Bot from "./cpdd/Bot";

    export default {
        name: "Home",
        components: {
            Top:Top,
            Mid:Mid,
            Bot:Bot
        }
    }
</script>

<style scoped>

</style>
