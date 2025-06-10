// TODO: i18n - processed
/**
 * Frontend Distributed Tracing Service
 * Provides OpenTelemetry instrumentation for React applications
 */
import { v4 as uuidv4 } from 'uuid';
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { BatchSpanProcessor, ConsoleSpanExporter } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';
import { getWebAutoInstrumentations } from '@opentelemetry/auto-instrumentations-web';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { XMLHttpRequestInstrumentation } from '@opentelemetry/instrumentation-xml-http-request';
import { UserInteractionInstrumentation } from '@opentelemetry/instrumentation-user-interaction';
import { DocumentLoadInstrumentation } from '@opentelemetry/instrumentation-document-load';
import { trace, context, propagation, SpanStatusCode, SpanKind } from '@opentelemetry/api';import { useTranslation } from "react-i18next";
class FrontendTracingService {
  constructor() {
    this.tracer = null;
    this.enabled = false;
    this.correlationId = null;
    this.requestId = null;
    this.userContext = null;
    // Configuration
    this.serviceName = 'bdc-frontend';
    this.serviceVersion = '1.0.0';
    this.environment = import.meta.env.VITE_ENVIRONMENT || 'development';
    this.otlpEndpoint = import.meta.env.VITE_OTEL_ENDPOINT || 'http://localhost:4318/v1/traces';
    this.jaegerEndpoint = import.meta.env.VITE_JAEGER_ENDPOINT || 'http://localhost:14268/api/traces';
    this.sampleRate = parseFloat(import.meta.env.VITE_TRACING_SAMPLE_RATE || '0.1');
    // Initialize if tracing is enabled
    if (import.meta.env.VITE_TRACING_ENABLED !== 'false') {
      this.initialize();
    }
  }
  initialize() {
    try {
      // Create resource
      const resource = Resource.default().merge(
        new Resource({
          [SemanticResourceAttributes.SERVICE_NAME]: this.serviceName,
          [SemanticResourceAttributes.SERVICE_VERSION]: this.serviceVersion,
          [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: this.environment,
          [SemanticResourceAttributes.SERVICE_NAMESPACE]: 'bdc',
          [SemanticResourceAttributes.SERVICE_INSTANCE_ID]: `${this.serviceName}-${uuidv4().slice(0, 8)}`
        })
      );
      // Create tracer provider
      const provider = new WebTracerProvider({
        resource,
        sampler: {
          shouldSample: () => ({
            decision: Math.random() < this.sampleRate ? 1 : 0 // SamplingDecision.RECORD_AND_SAMPLE : SamplingDecision.NOT_RECORD
          })
        }
      });
      // Create exporters
      const exporters = [];
      // OTLP exporter
      if (this.otlpEndpoint) {
        exporters.push(
          new OTLPTraceExporter({
            url: this.otlpEndpoint,
            headers: {
              'api-key': import.meta.env.VITE_OTEL_API_KEY || 'demo'
            }
          })
        );
      }
      // Jaeger exporter
      if (this.jaegerEndpoint) {
        exporters.push(
          new JaegerExporter({
            endpoint: this.jaegerEndpoint
          })
        );
      }
      // Console exporter for development
      if (this.environment === 'development') {
        exporters.push(new ConsoleSpanExporter());
      }
      // Add exporters
      exporters.forEach((exporter) => {
        provider.addSpanProcessor(
          new BatchSpanProcessor(exporter, {
            maxQueueSize: 2048,
            maxExportBatchSize: 512,
            scheduledDelayMillis: 5000,
            exportTimeoutMillis: 30000
          })
        );
      });
      // Register the provider
      provider.register();
      // Get tracer
      this.tracer = trace.getTracer(this.serviceName, this.serviceVersion);
      // Register instrumentations
      this.registerInstrumentations();
      this.enabled = true;
    } catch (error) {
      console.error('[Tracing] Initialization failed:', error);
      this.enabled = false;
    }
  }
  registerInstrumentations() {
    try {
      // Register auto-instrumentations
      registerInstrumentations({
        instrumentations: [
        // Document load instrumentation
        new DocumentLoadInstrumentation({
          ignoreNetworkEvents: false
        }),
        // Fetch instrumentation
        new FetchInstrumentation({
          propagateTraceHeaderCorsUrls: [
          /^https?:\/\/localhost/,
          /^https?:\/\/.*\.bdc\.com/],

          clearTimingResources: true,
          applyCustomAttributesOnSpan: (span, request, result) => {
            // Add custom attributes
            span.setAttributes({
              'http.request.correlation_id': this.getCorrelationId(),
              'http.request.request_id': this.getRequestId(),
              'user.id': this.userContext?.user_id,
              'user.role': this.userContext?.role
            });
            // Add response attributes
            if (result instanceof Response) {
              span.setAttributes({
                'http.response.size': parseInt(result.headers.get('content-length') || '0'),
                'http.response.correlation_id': result.headers.get('x-correlation-id'),
                'http.response.trace_id': result.headers.get('x-trace-id')
              });
            }
          },
          requestHook: (span, request) => {
            // Add request headers for tracing
            const headers = this.injectHeaders();
            Object.entries(headers).forEach(([key, value]) => {
              if (request.headers) {
                request.headers.set(key, value);
              }
            });
          }
        }),
        // XMLHttpRequest instrumentation
        new XMLHttpRequestInstrumentation({
          propagateTraceHeaderCorsUrls: [
          /^https?:\/\/localhost/,
          /^https?:\/\/.*\.bdc\.com/]

        }),
        // User interaction instrumentation
        new UserInteractionInstrumentation({
          eventNames: ['click', 'submit', 'keydown']
        })]

      });
    } catch (error) {
      console.error('[Tracing] Auto-instrumentation failed:', error);
    }
  }
  generateCorrelationId() {
    return `bdc_${uuidv4().replace(/-/g, '')}`;
  }
  generateRequestId() {
    return `req_${Date.now()}_${uuidv4().slice(0, 8)}`;
  }
  getCorrelationId() {
    if (!this.correlationId) {
      this.correlationId = this.generateCorrelationId();
    }
    return this.correlationId;
  }
  setCorrelationId(correlationId) {
    this.correlationId = correlationId;
    // Store in session storage for persistence
    try {
      sessionStorage.setItem('bdc_correlation_id', correlationId);
    } catch (e) {

      // Session storage not available
    }}
  getRequestId() {
    if (!this.requestId) {
      this.requestId = this.generateRequestId();
    }
    return this.requestId;
  }
  setRequestId(requestId) {
    this.requestId = requestId;
  }
  setUserContext(userData) {
    this.userContext = userData;
    // Add to current span if available
    const span = trace.getActiveSpan();
    if (span) {
      span.setAttributes({
        'user.id': userData.user_id,
        'user.email': userData.email,
        'user.role': userData.role
      });
    }
  }
  createSpan(name, kind = SpanKind.INTERNAL, attributes = {}) {
    if (!this.enabled || !this.tracer) {
      return trace.wrapSpanContext({
        traceId: '00000000000000000000000000000000',
        spanId: '0000000000000000',
        traceFlags: 0
      });
    }
    const span = this.tracer.startSpan(name, {
      kind,
      attributes: {
        'service.name': this.serviceName,
        'service.version': this.serviceVersion,
        'deployment.environment': this.environment,
        'correlation_id': this.getCorrelationId(),
        'request_id': this.getRequestId(),
        ...attributes
      }
    });
    // Add user context if available
    if (this.userContext) {
      span.setAttributes({
        'user.id': this.userContext.user_id,
        'user.role': this.userContext.role
      });
    }
    return span;
  }
  traceOperation(operationName, operation, kind = SpanKind.INTERNAL, attributes = {}) {
    const span = this.createSpan(operationName, kind, attributes);
    return context.with(trace.setSpan(context.active(), span), () => {
      try {
        const startTime = performance.now();
        const result = operation(span);
        // Handle async operations
        if (result && typeof result.then === 'function') {
          return result.
          then((res) => {
            const duration = performance.now() - startTime;
            span.setAttributes({
              'operation.duration': duration,
              'operation.result': 'success'
            });
            span.setStatus({ code: SpanStatusCode.OK });
            span.end();
            return res;
          }).
          catch((error) => {
            const duration = performance.now() - startTime;
            span.setAttributes({
              'operation.duration': duration,
              'operation.result': 'error',
              'error.message': error.message
            });
            span.recordException(error);
            span.setStatus({
              code: SpanStatusCode.ERROR,
              message: error.message
            });
            span.end();
            throw error;
          });
        } else {
          // Synchronous operation
          const duration = performance.now() - startTime;
          span.setAttributes({
            'operation.duration': duration,
            'operation.result': 'success'
          });
          span.setStatus({ code: SpanStatusCode.OK });
          span.end();
          return result;
        }
      } catch (error) {
        span.recordException(error);
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error.message
        });
        span.end();
        throw error;
      }
    });
  }
  tracePageLoad(pageName, routeParams = {}) {
    return this.traceOperation(
      `page_load`,
      (span) => {
        span.setAttributes({
          'page.name': pageName,
          'page.url': window.location.href,
          'page.referrer': document.referrer,
          'page.route_params': JSON.stringify(routeParams)
        });
        // Add performance metrics
        if (performance.navigation) {
          span.setAttributes({
            'page.navigation_type': performance.navigation.type,
            'page.redirect_count': performance.navigation.redirectCount
          });
        }
        // Add timing metrics
        if (performance.timing) {
          const timing = performance.timing;
          span.setAttributes({
            'page.dom_loading': timing.domLoading - timing.navigationStart,
            'page.dom_interactive': timing.domInteractive - timing.navigationStart,
            'page.dom_complete': timing.domComplete - timing.navigationStart,
            'page.load_complete': timing.loadEventEnd - timing.navigationStart
          });
        }
      },
      SpanKind.CLIENT,
      { 'operation.type': 'page_load' }
    );
  }
  traceUserAction(actionName, elementInfo = {}) {
    return this.traceOperation(
      `user_action.${actionName}`,
      (span) => {
        span.setAttributes({
          'user.action': actionName,
          'element.tag': elementInfo.tagName,
          'element.id': elementInfo.id,
          'element.class': elementInfo.className,
          'element.text': elementInfo.textContent?.slice(0, 100)
        });
      },
      SpanKind.CLIENT,
      { 'operation.type': 'user_interaction' }
    );
  }
  traceApiCall(method, url, requestData = null) {
    return this.traceOperation(
      `api_call.${method.toUpperCase()}`,
      (span) => {
        span.setAttributes({
          'http.method': method.toUpperCase(),
          'http.url': url,
          'http.request.size': requestData ? JSON.stringify(requestData).length : 0
        });
      },
      SpanKind.CLIENT,
      { 'operation.type': 'api_call' }
    );
  }
  traceError(error, context = {}) {
    return this.traceOperation(
      'error',
      (span) => {
        span.recordException(error);
        span.setAttributes({
          'error.type': error.constructor.name,
          'error.message': error.message,
          'error.stack': error.stack,
          'error.context': JSON.stringify(context)
        });
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error.message
        });
      },
      SpanKind.INTERNAL,
      { 'operation.type': 'error' }
    );
  }
  injectHeaders(headers = {}) {
    // Add correlation and request IDs
    headers['X-Correlation-ID'] = this.getCorrelationId();
    headers['X-Request-ID'] = this.getRequestId();
    // Add user context
    if (this.userContext) {
      headers['X-User-ID'] = this.userContext.user_id;
      headers['X-User-Role'] = this.userContext.role;
    }
    // Inject OpenTelemetry context
    const activeContext = context.active();
    propagation.inject(activeContext, headers);
    return headers;
  }
  extractHeaders(headers) {
    // Extract correlation ID
    const correlationId = headers['X-Correlation-ID'] || headers['x-correlation-id'];
    if (correlationId) {
      this.setCorrelationId(correlationId);
    }
    // Extract request ID
    const requestId = headers['X-Request-ID'] || headers['x-request-id'];
    if (requestId) {
      this.setRequestId(requestId);
    }
    // Extract OpenTelemetry context
    return propagation.extract(context.active(), headers);
  }
  // React integration helpers
  withTracing(WrappedComponent, componentName) {
    return function TracedComponent(props) {
      const span = this.createSpan(
        `component.${componentName}`,
        SpanKind.INTERNAL,
        { 'component.name': componentName }
      );
      return context.with(trace.setSpan(context.active(), span), () => {
        try {
          const result = WrappedComponent(props);
          span.setStatus({ code: SpanStatusCode.OK });
          span.end();
          return result;
        } catch (error) {
          span.recordException(error);
          span.setStatus({
            code: SpanStatusCode.ERROR,
            message: error.message
          });
          span.end();
          throw error;
        }
      });
    };
  }
  // Performance monitoring
  reportWebVitals(metric) {
    const span = this.createSpan(
      `web_vital.${metric.name}`,
      SpanKind.INTERNAL,
      {
        'web_vital.name': metric.name,
        'web_vital.value': metric.value,
        'web_vital.id': metric.id,
        'web_vital.delta': metric.delta
      }
    );
    span.setStatus({ code: SpanStatusCode.OK });
    span.end();
  }
}
// Create global instance
const tracingService = new FrontendTracingService();
// Export convenience functions
export const createSpan = (name, kind, attributes) =>
tracingService.createSpan(name, kind, attributes);
export const traceOperation = (name, operation, kind, attributes) =>
tracingService.traceOperation(name, operation, kind, attributes);
export const tracePageLoad = (pageName, routeParams) =>
tracingService.tracePageLoad(pageName, routeParams);
export const traceUserAction = (actionName, elementInfo) =>
tracingService.traceUserAction(actionName, elementInfo);
export const traceApiCall = (method, url, requestData) =>
tracingService.traceApiCall(method, url, requestData);
export const traceError = (error, context) =>
tracingService.traceError(error, context);
export const setUserContext = (userData) =>
tracingService.setUserContext(userData);
export const getCorrelationId = () =>
tracingService.getCorrelationId();
export const setCorrelationId = (correlationId) =>
tracingService.setCorrelationId(correlationId);
export const injectHeaders = (headers) =>
tracingService.injectHeaders(headers);
export const extractHeaders = (headers) =>
tracingService.extractHeaders(headers);
export const reportWebVitals = (metric) =>
tracingService.reportWebVitals(metric);
export default tracingService;