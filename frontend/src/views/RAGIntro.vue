<template>
  <div class="rag-intro-container">
    <h1>{{ $t('ragIntro.title') }}</h1>
    <p>
      {{ $t('ragIntro.p1') }}
    </p>
    <p>
      {{ $t('ragIntro.p2') }}
    </p>
    <p>
      {{ $t('ragIntro.p3') }}
    </p>
    <p>
      {{ $t('ragIntro.p4') }}
    </p>
    <ul>
      <li><b>{{ $t('ragIntro.li1').split('：')[0] }}：</b>{{ $t('ragIntro.li1').split('：')[1] }}</li>
      <li><b>{{ $t('ragIntro.li2').split('：')[0] }}：</b>{{ $t('ragIntro.li2').split('：')[1] }}</li>
      <li><b>{{ $t('ragIntro.li3').split('：')[0] }}：</b>{{ $t('ragIntro.li3').split('：')[1] }}</li>
      <li><b>{{ $t('ragIntro.li4').split('：')[0] }}：</b>{{ $t('ragIntro.li4').split('：')[1] }}</li>
    </ul>
    <p>
      {{ $t('ragIntro.p5') }}
    </p>
    <ul>
      <li><b>{{ $t('ragIntro.li5').split('：')[0] }}：</b>{{ $t('ragIntro.li5').split('：')[1] }}</li>
      <li><b>{{ $t('ragIntro.li6').split('：')[0] }}：</b>{{ $t('ragIntro.li6').split('：')[1] }}</li>
    </ul>
    <p>
      {{ $t('ragIntro.p6') }}
    </p>
    <p>
      {{ $t('ragIntro.p7') }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
// Script setup for RAGIntro view
</script>

<style scoped>
.rag-intro-container {
  padding: 20px;
  line-height: 1.6;
}

.rag-intro-container h1 {
  color: var(--el-text-color-primary);
  margin-bottom: 20px;
}

.rag-intro-container p {
  margin-bottom: 15px;
  color: var(--el-text-color-regular);
}

.rag-intro-container ul {
  margin-bottom: 15px;
  padding-left: 20px;
}

.rag-intro-container li {
  margin-bottom: 5px;
  color: var(--el-text-color-regular);
}

.rag-intro-container b {
    color: var(--el-text-color-primary);
}
</style>