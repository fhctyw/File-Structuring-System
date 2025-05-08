<script setup lang="ts">
import { computed, watch } from 'vue'
import { useDynamicForm, type JsonSchema } from '../composables/useDynamicForm'

const props = defineProps<{
  schema: JsonSchema
  modelValue: Record<string, any>
}>()

const emit = defineEmits(['update:modelValue', 'submit'])

// Use the dynamic form composable
const { formData, errors, touched, validate, touchField, getFieldError } = 
  useDynamicForm(props.schema)

// Sync formData with modelValue prop (two-way binding)
watch(() => props.modelValue, (newValue) => {
  Object.keys(formData).forEach(key => {
    if (newValue && newValue[key] !== undefined) {
      formData[key] = newValue[key]
    }
  })
}, { deep: true, immediate: true })

watch(formData, (newValue) => {
  emit('update:modelValue', { ...newValue })
}, { deep: true })

// Handle form submission
const submitForm = () => {
  Object.keys(formData).forEach(field => {
    touchField(field)
  })
  
  if (validate()) {
    emit('submit', { ...formData })
  }
}

// Get field component based on property type
const getFieldComponent = (key: string, property: any) => {
  // Handle enum fields as select
  if (property.enum) {
    return 'select'
  }
  
  // Map JSON schema types to form field types
  switch (property.type) {
    case 'string':
      return 'text'
    case 'number':
    case 'integer':
      return 'number'
    case 'boolean':
      return 'checkbox'
    case 'object':
      return 'object'
    case 'array':
      return 'array'
    default:
      return 'text'
  }
}

// Format property description for display
const formatDescription = (description?: string) => {
  return description || ''
}
</script>

<template>
  <form @submit.prevent="submitForm" class="dynamic-form">
    <div
      v-for="(property, key) in schema.properties"
      :key="key"
      class="form-field"
    >
      <label :for="key" class="field-label">
        {{ key }}
        <span v-if="schema.required?.includes(key)" class="required">*</span>
      </label>
      
      <div class="field-description" v-if="property.description">
        {{ formatDescription(property.description) }}
      </div>
      
      <!-- Text input -->
      <input
        v-if="getFieldComponent(key, property) === 'text'"
        :id="key"
        v-model="formData[key]"
        type="text"
        class="form-input"
        :class="{ 'has-error': getFieldError(key) }"
        @blur="touchField(key)"
      />
      
      <!-- Number input -->
      <input
        v-else-if="getFieldComponent(key, property) === 'number'"
        :id="key"
        v-model.number="formData[key]"
        type="number"
        class="form-input"
        :class="{ 'has-error': getFieldError(key) }"
        :min="property.minimum"
        :max="property.maximum"
        @blur="touchField(key)"
      />
      
      <!-- Select/dropdown -->
      <select
        v-else-if="getFieldComponent(key, property) === 'select'"
        :id="key"
        v-model="formData[key]"
        class="form-select"
        :class="{ 'has-error': getFieldError(key) }"
        @blur="touchField(key)"
      >
        <option value="" disabled>Please select</option>
        <option
          v-for="option in property.enum"
          :key="option"
          :value="option"
        >
          {{ option }}
        </option>
      </select>
      
      <!-- Checkbox -->
      <div
        v-else-if="getFieldComponent(key, property) === 'checkbox'"
        class="checkbox-field"
      >
        <input
          :id="key"
          v-model="formData[key]"
          type="checkbox"
          class="form-checkbox"
          @blur="touchField(key)"
        />
        <label :for="key" class="checkbox-label">{{ formatDescription(property.description) }}</label>
      </div>
      
      <!-- Object fields handled recursively (TODO: implement for complex nested objects) -->
      <div v-else-if="getFieldComponent(key, property) === 'object'" class="object-field">
        <div class="field-description">Complex object field (to be implemented)</div>
      </div>
      
      <!-- Array fields handled recursively (TODO: implement for arrays) -->
      <div v-else-if="getFieldComponent(key, property) === 'array'" class="array-field">
        <div class="field-description">Array field (to be implemented)</div>
      </div>
      
      <!-- Error message -->
      <div v-if="getFieldError(key)" class="field-error">
        {{ getFieldError(key) }}
      </div>
    </div>
    
    <!-- Form controls -->
    <div class="form-actions">
      <slot name="actions">
        <button type="submit" class="submit-button">Submit</button>
      </slot>
    </div>
  </form>
</template>

<style scoped>
.dynamic-form {
  background-color: var(--color-background);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-md);
}

.form-field {
  margin-bottom: var(--space-6);
}

.field-label {
  display: block;
  font-weight: 500;
  margin-bottom: var(--space-2);
  color: var(--color-text);
}

.required {
  color: var(--color-error);
  margin-left: var(--space-1);
}

.field-description {
  font-size: 0.875rem;
  color: var(--color-text-light);
  margin-bottom: var(--space-2);
}

.form-input,
.form-select {
  width: 100%;
  padding: var(--space-3);
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-md);
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.has-error {
  border-color: var(--color-error) !important;
}

.field-error {
  color: var(--color-error);
  font-size: 0.875rem;
  margin-top: var(--space-2);
}

.checkbox-field {
  display: flex;
  align-items: center;
}

.form-checkbox {
  margin-right: var(--space-3);
}

.checkbox-label {
  font-weight: normal;
}

.object-field,
.array-field {
  padding: var(--space-4);
  border: 1px dashed #e2e8f0;
  border-radius: var(--radius-md);
}

.form-actions {
  margin-top: var(--space-8);
  display: flex;
  justify-content: flex-end;
}

.submit-button {
  background-color: var(--color-primary);
  color: white;
  padding: var(--space-3) var(--space-6);
  border: none;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit-button:hover {
  background-color: var(--color-primary-dark);
}
</style>