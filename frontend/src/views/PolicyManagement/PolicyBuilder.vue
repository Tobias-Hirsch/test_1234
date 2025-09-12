<template>
  <div class="policy-builder-container">
    <el-form :model="policy" label-position="top">
      <h3>基础信息</h3>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="策略名称">
            <el-input v-model="policy.name" placeholder="例如：允许经理查看所有文档"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="效果">
            <el-select v-model="policy.effect" style="width: 100%;">
              <el-option label="允许 (Allow)" value="allow"></el-option>
              <el-option label="拒绝 (Deny)" value="deny"></el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="描述">
        <el-input type="textarea" v-model="policy.description" placeholder="详细说明此策略的目的和范围"></el-input>
      </el-form-item>

      <el-divider></el-divider>

      <h3>规则定义：构建一个策略句子</h3>
      <p class="policy-sentence">
        此策略 <strong>{{ policy.effect === 'allow' ? '允许' : '拒绝' }}</strong>
        <strong>[主体]</strong>
        对 <strong>[资源]</strong>
        执行 <strong>[操作]</strong>
        在 <strong>[条件]</strong> 满足时。
      </p>

      <!-- 主体 (Subjects) -->
      <div class="rule-block">
        <h4>主体 (Subject)</h4>
        <p class="description">定义“谁”受此策略影响。一个主体必须满足 <strong>所有</strong> 以下规则。</p>
        
        <div v-for="(rule, index) in subjectRules" :key="index" class="rule-row">
          <el-select v-model="rule.key" placeholder="选择主体属性" filterable style="width: 250px;" @change="onAttributeChange(rule, 'subject')">
            <el-option
              v-for="attr in subjectAttributes"
              :key="attr.key"
              :label="attr.name"
              :value="attr.key">
              <span style="float: left">{{ attr.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ attr.key }}</span>
            </el-option>
          </el-select>

          <el-select v-model="rule.operator" placeholder="选择操作符" style="width: 150px; margin-left: 10px;">
            <el-option
              v-for="op in getOperatorsForType(rule.type)"
              :key="op.value"
              :label="op.label"
              :value="op.value">
            </el-option>
          </el-select>

          <el-select
            v-if="isValueASelection(rule.key)"
            v-model="rule.value"
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入值"
            style="width: 300px; margin-left: 10px;"
          >
            <el-option
              v-for="item in getValueOptions(rule.key)"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-input v-else v-model="rule.value" placeholder="输入期望值" style="width: 300px; margin-left: 10px;" />

          <el-button type="danger" :icon="ElIconDelete" circle plain @click="removeSubjectRule(index)" style="margin-left: 10px;" />
        </div>

        <el-button @click="addSubjectRule" :icon="ElIconPlus">添加主体规则</el-button>
      </div>

      <!-- 资源 (Resources) -->
      <div class="rule-block">
        <h4>资源 (Resource)</h4>
        <p class="description">定义此策略应用于“什么事物”。一个资源必须满足 <strong>所有</strong> 以下规则。</p>

        <div v-for="(rule, index) in resourceRules" :key="index" class="rule-row">
          <el-select v-model="rule.key" placeholder="选择资源属性" filterable style="width: 250px;" @change="onAttributeChange(rule, 'resource')">
            <el-option
              v-for="attr in resourceAttributes"
              :key="attr.key"
              :label="attr.name"
              :value="attr.key">
              <span style="float: left">{{ attr.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ attr.key }}</span>
            </el-option>
          </el-select>

          <el-select v-model="rule.operator" placeholder="选择操作符" style="width: 150px; margin-left: 10px;">
            <el-option
              v-for="op in getOperatorsForType(rule.type)"
              :key="op.value"
              :label="op.label"
              :value="op.value">
            </el-option>
          </el-select>

          <el-select
            v-if="isValueASelection(rule.key)"
            v-model="rule.value"
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入值"
            style="width: 300px; margin-left: 10px;"
          >
            <el-option
              v-for="item in getValueOptions(rule.key)"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-input v-else v-model="rule.value" placeholder="输入期望值" style="width: 300px; margin-left: 10px;" />

          <el-button type="danger" :icon="ElIconDelete" circle plain @click="removeResourceRule(index)" style="margin-left: 10px;" />
        </div>

        <el-button @click="addResourceRule" :icon="ElIconPlus">添加资源规则</el-button>
      </div>

      <!-- 操作 (Actions) -->
      <div class="rule-block">
        <h4>操作 (Action)</h4>
        <p class="description">定义允许或拒绝的具体操作。</p>
        <el-checkbox-group v-model="policy.actions">
          <el-checkbox v-for="action in availableActions" :key="action" :label="action" :value="action">
            {{ action }}
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <!-- 条件 (Conditions) - Optional -->
      <div class="rule-block">
        <h4>条件 (Condition) <el-tag size="small">可选</el-tag></h4>
        <p class="description">定义策略生效所需的额外约束。一个策略必须满足 <strong>所有</strong> 以下条件。</p>
        
        <div v-for="(rule, index) in conditionRules" :key="index" class="rule-row">
          <el-select v-model="rule.key" placeholder="选择属性" filterable style="width: 250px;" @change="onAttributeChange(rule, 'condition')">
            <el-option
              v-for="attr in conditionAttributes"
              :key="attr.key"
              :label="attr.name"
              :value="attr.key">
              <span style="float: left">{{ attr.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ attr.key }}</span>
            </el-option>
          </el-select>

          <el-select v-model="rule.operator" placeholder="选择操作符" style="width: 150px; margin-left: 10px;">
            <el-option
              v-for="op in getOperatorsForType(rule.type)"
              :key="op.value"
              :label="op.label"
              :value="op.value">
            </el-option>
          </el-select>

          <el-select
            v-if="isValueASelection(rule.key)"
            v-model="rule.value"
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入值"
            style="width: 300px; margin-left: 10px;"
          >
            <el-option
              v-for="item in getValueOptions(rule.key)"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-input v-else v-model="rule.value" placeholder="输入期望值或属性key (e.g. resource.owner_id)" style="width: 300px; margin-left: 10px;" />

          <el-button type="danger" :icon="ElIconDelete" circle plain @click="removeConditionRule(index)" style="margin-left: 10px;" />
        </div>

        <el-button @click="addConditionRule" :icon="ElIconPlus">添加条件规则</el-button>
      </div>

      <el-divider />

      <div class="form-footer">
        <el-button @click="cancel">取消</el-button>
        <el-button type="primary" @click="savePolicy">保存策略</el-button>
      </div>

    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, PropType } from 'vue';
import { get, getRoles } from '@/services/apiService';
import { ElMessage } from 'element-plus';
import { Delete as ElIconDelete, Plus as ElIconPlus } from '@element-plus/icons-vue';

// Interface for a single rule in the builder
interface Rule {
  key: string;
  operator: string;
  value: string;
  type: string; // The data type of the attribute, e.g., 'string', 'integer'
}

// Interface for the policy object being built
interface PolicyBuilderState {
  id?: number;
  name: string;
  description: string;
  effect: 'allow' | 'deny';
  actions: string[];
  subjects: any[]; // To be defined with more specific types
  resources: any[]; // To be defined with more specific types
  conditions?: any[]; // To be defined with more specific types
  is_active: boolean;
}

// Props for the component, e.g., to load an existing policy for editing
const props = defineProps({
  policyId: {
    type: Number as PropType<number | null>,
    default: null,
  },
  initialData: {
    type: Object as PropType<PolicyBuilderState | null>,
    default: null,
  },
});

const emit = defineEmits(['save', 'cancel']);

const policy = ref<PolicyBuilderState>({
  name: '',
  description: '',
  effect: 'allow',
  actions: [],
  subjects: [],
  resources: [],
  conditions: [],
  is_active: true,
});

// --- Start of Subject Rules Logic ---
const subjectRules = ref<Rule[]>([]);

const subjectAttributes = computed(() =>
  availableAttributes.value.filter((attr: any) => attr.category === 'subject')
);

const addSubjectRule = () => {
  subjectRules.value.push({ key: '', operator: 'equals', value: '', type: 'string' });
};

const removeSubjectRule = (index: number) => {
  subjectRules.value.splice(index, 1);
};

watch(subjectRules, (newRules) => {
  policy.value.subjects = newRules
    .filter(rule => rule.key && rule.value)
    .map(rule => ({
      key: rule.key,
      operator: rule.operator,
      value: [rule.value] // Backend expects a list of strings
    }));
}, { deep: true });
// --- End of Subject Rules Logic ---

// --- Start of Resource Rules Logic ---
const resourceRules = ref<Rule[]>([]);

const resourceAttributes = computed(() =>
  availableAttributes.value.filter((attr: any) => attr.category === 'resource')
);

const addResourceRule = () => {
  resourceRules.value.push({ key: '', operator: 'equals', value: '', type: 'string' });
};

const removeResourceRule = (index: number) => {
  resourceRules.value.splice(index, 1);
};

watch(resourceRules, (newRules) => {
  policy.value.resources = newRules
    .filter(rule => rule.key && rule.value)
    .map(rule => ({
      key: rule.key,
      operator: rule.operator,
      value: [rule.value] // Backend expects a list of strings
    }));
}, { deep: true });
// --- End of Resource Rules Logic ---

// --- Start of Condition Rules Logic ---
const conditionRules = ref<Rule[]>([]);

// Conditions can use any attribute
const conditionAttributes = computed(() => availableAttributes.value);

const addConditionRule = () => {
  conditionRules.value.push({ key: '', operator: 'equals', value: '', type: 'string' });
};

const removeConditionRule = (index: number) => {
  conditionRules.value.splice(index, 1);
};

watch(conditionRules, (newRules) => {
  if (newRules.length === 0 || newRules.every(rule => !rule.key || !rule.value)) {
    policy.value.conditions = [];
    return;
  }
  policy.value.conditions = newRules
    .filter(rule => rule.key && rule.value)
    .map(rule => ({
      key: rule.key, // 'key' is the correct field name per schema
      operator: rule.operator,
      value: [rule.value] // Backend expects a list of strings
    }));
}, { deep: true });
// --- End of Condition Rules Logic ---


// Data stores for the "vocabulary" from the backend
const availableAttributes = ref<any[]>([]);
const availableActions = ref([]);
const availableResourceTypes = ref([]);
const availableRoles = ref<{ name: string }[]>([]);

// Fetching the vocabulary from our new backend APIs
const fetchVocabulary = async () => {
  try {
    const [attributes, actions, resourceTypes, roles] = await Promise.all([
      get('/abac/attributes'),
      get('/abac/actions'),
      get('/abac/resource-types'),
      getRoles(),
    ]);
    availableAttributes.value = attributes;
    availableActions.value = actions;
    availableResourceTypes.value = resourceTypes;
    availableRoles.value = roles;
  } catch (error) {
    console.error('Failed to fetch policy vocabulary:', error);
    ElMessage.error('加载策略构建器所需数据失败');
  }
};

const setPolicyForEditing = (p: any) => {
  // This function takes a policy object from the API and populates the builder's state.
  policy.value.id = p.id;
  policy.value.name = p.name;
  policy.value.description = p.description;
  policy.value.effect = p.effect;
  policy.value.actions = p.actions;
  policy.value.is_active = !!p.is_active;

  // Reverse-transform subjects from API format to UI format (Rule[])
  subjectRules.value = p.subjects.map((filter: any) => {
    const attribute = availableAttributes.value.find(attr => attr.key === filter.key);
    return {
      key: filter.key,
      operator: filter.operator,
      value: filter.value[0] || '', // Take the first value
      type: attribute ? attribute.type : 'string',
    };
  });

  // Reverse-transform resources
  resourceRules.value = p.resources.map((filter: any) => {
    const attribute = availableAttributes.value.find(attr => attr.key === filter.key);
    return {
      key: filter.key,
      operator: filter.operator,
      value: filter.value[0] || '',
      type: attribute ? attribute.type : 'string',
    };
  });

  // Reverse-transform conditions
  // The API response uses 'conditions', which is correct.
  conditionRules.value = (p.conditions || []).map((filter: any) => {
    const attribute = availableAttributes.value.find(attr => attr.key === filter.key);
    return {
      key: filter.key,
      operator: filter.operator,
      value: filter.value[0] || '',
      type: attribute ? attribute.type : 'string',
    };
  });
};

onMounted(async () => {
  // Always fetch vocabulary first
  await fetchVocabulary();

  if (props.initialData) {
    // 1. Priority: Use initial data if provided (for cloning)
    setPolicyForEditing(props.initialData);
  } else if (props.policyId) {
    // 2. Fallback: Fetch policy by ID if provided (for editing)
    try {
      const existingPolicy = await get(`/policies/${props.policyId}`);
      if (existingPolicy) {
        setPolicyForEditing(existingPolicy);
      }
    } catch (error) {
      ElMessage.error('加载策略数据失败');
      console.error(`Failed to fetch policy ${props.policyId} for editing:`, error);
    }
  }
  // 3. If neither, it's a new policy, and vocabulary is already fetched.
});

const savePolicy = () => {
  // Basic validation
  if (!policy.value.name) {
    ElMessage.warning('策略名称不能为空');
    return;
  }
  if (policy.value.actions.length === 0) {
    ElMessage.warning('请至少选择一个操作');
    return;
  }

  // The policy ref already contains the structured data.
  // We just need to emit it.
  emit('save', { ...policy.value });
};

const cancel = () => {
  emit('cancel');
};

// --- Helper functions for dynamic UI ---
const onAttributeChange = (rule: Rule, category: 'subject' | 'resource' | 'condition') => {
  const selectedAttr = availableAttributes.value.find(attr => attr.key === rule.key);
  if (selectedAttr) {
    rule.type = selectedAttr.type;
    // Reset operator and value
    rule.operator = getOperatorsForType(rule.type)[0].value;
    rule.value = '';
  }
};

const getOperatorsForType = (type: string) => {
  const commonOperators = [
    { label: '等于', value: 'eq' },
    { label: '不等于', value: 'not_eq' }, // Assuming backend supports 'not_eq'
  ];
  const arrayOperators = [
    { label: '包含其中之一', value: 'in' },
    { label: '不包含', value: 'not_in' }, // Assuming backend supports 'not_in'
  ];
  const numericOperators = [
    { label: '大于', value: 'greater_than' },
    { label: '小于', value: 'less_than' },
  ];

  switch (type) {
    case 'array_string':
    case 'array_integer':
      return [...commonOperators, ...arrayOperators];
    case 'integer':
      return [...commonOperators, ...numericOperators];
    default: // string, etc.
      return commonOperators;
  }
};
// --- End of Helper functions ---

const isValueASelection = (key: string) => {
  return key === 'user.roles' || key === 'resource.type';
};

const getValueOptions = (key: string) => {
  if (key === 'user.roles') {
    return availableRoles.value.map(role => ({ label: role.name, value: role.name }));
  }
  if (key === 'resource.type') {
    return availableResourceTypes.value.map((rt: string) => ({ label: rt, value: rt }));
  }
  return [];
};

</script>

<style scoped>
.policy-builder-container {
  padding: 20px;
}
.form-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
.rule-block {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
  background-color: #fafafa;
}
.rule-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.policy-sentence {
  font-size: 1.1em;
  color: #606266;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f0f9eb;
  border-left: 5px solid #67c23a;
}
.description {
  font-size: 0.9em;
  color: #909399;
  margin-top: 0;
}
h3, h4 {
    margin-bottom: 10px;
}
</style>