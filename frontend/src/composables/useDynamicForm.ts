import { ref, reactive, computed } from 'vue'

// Define types for JSON Schema properties
export interface SchemaProperty {
  type: string
  description?: string
  enum?: string[] | number[]
  default?: any
  minimum?: number
  maximum?: number
  items?: SchemaProperty
  properties?: Record<string, SchemaProperty>
  required?: string[]
}

export interface JsonSchema {
  type: string
  properties: Record<string, SchemaProperty>
  required?: string[]
}

export function useDynamicForm(schema: JsonSchema) {
  // Create reactive form data with default values
  const formData = reactive<Record<string, any>>({})
  const errors = ref<Record<string, string>>({})
  const touched = ref<Record<string, boolean>>({})
  
  // Extract default values from schema
  const initializeFormData = () => {
    if (!schema?.properties) return
    
    Object.entries(schema.properties).forEach(([key, prop]) => {
      if (prop.default !== undefined) {
        formData[key] = prop.default
      } else {
        // Set default values based on type
        switch (prop.type) {
          case 'string':
            formData[key] = ''
            break
          case 'number':
          case 'integer':
            formData[key] = 0
            break
          case 'boolean':
            formData[key] = false
            break
          case 'array':
            formData[key] = []
            break
          case 'object':
            formData[key] = {}
            break
        }
      }
    })
  }
  
  // Initialize form data when the schema changes
  const resetForm = () => {
    Object.keys(formData).forEach(key => {
      delete formData[key]
    })
    errors.value = {}
    touched.value = {}
    initializeFormData()
  }
  
  // Validate form data against schema
  const validate = () => {
    const newErrors: Record<string, string> = {}
    let isValid = true
    
    Object.entries(schema.properties).forEach(([key, prop]) => {
      // Check required fields
      if (schema.required?.includes(key) && 
          (formData[key] === undefined || formData[key] === '')) {
        newErrors[key] = 'Це поле є обов\'язковим'
        isValid = false
        return
      }
      
      // Skip validation if field is empty and not required
      if (formData[key] === undefined || formData[key] === '') {
        return
      }
      
      // Type validation
      switch (prop.type) {
        case 'number':
        case 'integer':
          if (typeof formData[key] !== 'number') {
            newErrors[key] = 'Має бути числом'
            isValid = false
          } else {
            // Range validation
            if (prop.minimum !== undefined && formData[key] < prop.minimum) {
              newErrors[key] = `Мінімальне значення ${prop.minimum}`
              isValid = false
            }
            if (prop.maximum !== undefined && formData[key] > prop.maximum) {
              newErrors[key] = `Максимальне значення ${prop.maximum}`
              isValid = false
            }
          }
          break
          
        case 'string':
          if (typeof formData[key] !== 'string') {
            newErrors[key] = 'Має бути текстом'
            isValid = false
          } else if (prop.enum && !prop.enum.includes(formData[key])) {
            newErrors[key] = 'Вибрано недопустимий варіант'
            isValid = false
          }
          break
      }
    })
    
    errors.value = newErrors
    return isValid
  }
  
  // Mark field as touched when user interacts with it
  const touchField = (field: string) => {
    touched.value[field] = true
  }
  
  // Get error for specific field
  const getFieldError = (field: string) => {
    return touched.value[field] ? errors.value[field] : ''
  }
  
  // Check if form is valid
  const isValid = computed(() => {
    return validate()
  })
  
  // Initialize form data
  initializeFormData()
  
  return {
    formData,
    errors,
    touched,
    validate,
    resetForm,
    touchField,
    getFieldError,
    isValid
  }
}