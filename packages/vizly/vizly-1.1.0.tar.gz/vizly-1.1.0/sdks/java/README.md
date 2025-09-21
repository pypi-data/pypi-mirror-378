# ☕ Vizly Java SDK

## **Enterprise Java Visualization with GPU Acceleration**

The **Vizly Java SDK** brings enterprise-grade visualization capabilities to Java 11+ applications with seamless Python integration, GPU acceleration, and enterprise security features. Perfect for large-scale Java deployments and Spring Boot applications.

[![Maven Central](https://img.shields.io/badge/Maven-Central-blue)](mailto:durai@infinidatum.net)
[![Java 11+](https://img.shields.io/badge/Java-11%2B-orange)](https://openjdk.java.net/)
[![Spring Boot](https://img.shields.io/badge/Spring-Boot-green)](https://spring.io/projects/spring-boot)

---

## 🚀 **Quick Start**

### **Installation via Maven**
```xml
<dependency>
    <groupId>com.infinidatum</groupId>
    <artifactId>vizly-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

### **Installation via Gradle**
```gradle
implementation 'com.infinidatum:vizly-sdk:1.0.0'
```

### **Hello World Example**
```java
import com.infinidatum.vizly.*;
import com.infinidatum.vizly.charts.LineChart;
import com.infinidatum.vizly.core.VizlyEngine;
import com.infinidatum.vizly.exceptions.VizlyException;
import com.infinidatum.vizly.types.*;

import java.util.Arrays;
import java.util.stream.IntStream;

public class HelloWorld {
    public static void main(String[] args) {
        try {
            // Initialize Vizly engine
            VizlyEngine engine = VizlyEngine.getInstance();
            EngineConfig config = new EngineConfig();
            config.setVerbose(true);

            engine.initialize(config);

            // Display system information
            SystemInfo sysInfo = engine.getSystemInfo();
            System.out.println("Vizly Version: " + sysInfo.getVersion());
            System.out.println("GPU Available: " + sysInfo.isGpuAvailable());
            System.out.println("VR Available: " + sysInfo.isVrAvailable());

            // Create chart configuration
            ChartConfig chartConfig = new ChartConfig();
            chartConfig.setWidth(800);
            chartConfig.setHeight(600);
            chartConfig.setEnableGpu(engine.isGpuAvailable());

            // Create and use line chart
            try (LineChart chart = new LineChart(chartConfig)) {
                // Generate sine wave data
                double[] x = IntStream.range(0, 100)
                    .mapToDouble(i -> i * Math.PI / 50.0)
                    .toArray();
                double[] y = Arrays.stream(x).map(Math::sin).toArray();

                // Plot data
                chart.plot(x, y, Color.BLUE, 2.0, "sin(x)");
                chart.setTitle("Vizly Java SDK - Hello World");
                chart.setAxisLabels("X (radians)", "Y");
                chart.showGrid(true);
                chart.showLegend(true);

                // Save chart
                chart.save("hello_world.png");

                System.out.println("✅ Chart created successfully!");
            }

        } catch (VizlyException e) {
            System.err.println("Vizly Error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            // Cleanup
            VizlyEngine.getInstance().shutdown();
        }
    }
}
```

---

## 🌟 **Key Features**

### **🚀 Enterprise Performance**
- **GPU Acceleration**: CUDA/OpenCL integration via JNI
- **Memory Management**: Automatic resource cleanup and monitoring
- **Thread Safety**: Concurrent chart generation capabilities
- **Connection Pooling**: Efficient Python process management

### **🎨 Professional Integration**
- **Spring Boot Support**: Auto-configuration and dependency injection
- **Microservices Ready**: Lightweight, containerized deployments
- **REST API Integration**: Direct chart generation endpoints
- **Database Connectivity**: JDBC, JPA, Hibernate compatibility

### **🔧 Enterprise Architecture**
- **Exception Handling**: Comprehensive error management
- **Logging Integration**: SLF4J, Logback, Log4j2 support
- **Configuration Management**: Properties, YAML, environment variables
- **Security**: Enterprise authentication and authorization

---

## 📊 **Chart Types & Examples**

### **LineChart - Financial Dashboard**
```java
import com.infinidatum.vizly.charts.LineChart;
import com.infinidatum.vizly.types.*;

@Service
public class FinancialDashboardService {

    private final VizlyEngine engine;
    private final ChartConfig defaultConfig;

    public FinancialDashboardService() throws VizlyException {
        this.engine = VizlyEngine.getInstance();
        engine.initialize();

        this.defaultConfig = new ChartConfig();
        defaultConfig.setWidth(1200);
        defaultConfig.setHeight(800);
        defaultConfig.setEnableGpu(engine.isGpuAvailable());
    }

    public byte[] createStockChart(List<StockData> stockData) throws VizlyException {
        try (LineChart chart = new LineChart(defaultConfig)) {
            // Extract time series data
            double[] timestamps = stockData.stream()
                .mapToDouble(data -> data.getTimestamp().toEpochMilli())
                .toArray();
            double[] prices = stockData.stream()
                .mapToDouble(StockData::getPrice)
                .toArray();
            double[] volumes = stockData.stream()
                .mapToDouble(StockData::getVolume)
                .toArray();

            // Create multiple series
            LineSeriesData priceData = new LineSeriesData();
            priceData.setX(timestamps);
            priceData.setY(prices);
            priceData.setColor(Color.BLUE);
            priceData.setLineWidth(2.0);
            priceData.setLabel("Price");

            LineSeriesData volumeData = new LineSeriesData();
            volumeData.setX(timestamps);
            volumeData.setY(volumes);
            volumeData.setColor(Color.RED);
            volumeData.setLineWidth(1.5);
            volumeData.setLabel("Volume");

            // Plot series
            chart.plotMultiple(Arrays.asList(priceData, volumeData));

            // Add technical indicators
            double[] movingAverage = calculateMovingAverage(prices, 20);
            chart.addTrendLine(timestamps, movingAverage, "linear", Color.GREEN);

            // Configure chart
            chart.setTitle("Real-time Stock Analysis");
            chart.setAxisLabels("Time", "Value");
            chart.showGrid(true);
            chart.showLegend(true);

            // Export as byte array for web response
            String base64Data = chart.exportBase64(300);
            return Base64.getDecoder().decode(base64Data);
        }
    }

    private double[] calculateMovingAverage(double[] prices, int period) {
        // Implementation for moving average calculation
        // ...
        return new double[0]; // Placeholder
    }
}
```

### **ScatterChart - Machine Learning Visualization**
```java
import com.infinidatum.vizly.charts.ScatterChart;

@Component
public class MLVisualizationService {

    public void visualizeClusteringResults(List<DataPoint> dataPoints,
                                         List<Integer> clusterLabels) throws VizlyException {

        ChartConfig config = new ChartConfig();
        config.setWidth(1000);
        config.setHeight(800);
        config.setEnableGpu(true); // Enable for large datasets

        try (ScatterChart scatter = new ScatterChart(config)) {
            // Group by cluster
            Map<Integer, List<DataPoint>> clusters = dataPoints.stream()
                .collect(Collectors.groupingBy(
                    point -> clusterLabels.get(dataPoints.indexOf(point))));

            Color[] clusterColors = {Color.RED, Color.BLUE, Color.GREEN,
                                   Color.ORANGE, Color.PURPLE};

            // Plot each cluster
            int colorIndex = 0;
            for (Map.Entry<Integer, List<DataPoint>> cluster : clusters.entrySet()) {
                double[] x = cluster.getValue().stream()
                    .mapToDouble(DataPoint::getX).toArray();
                double[] y = cluster.getValue().stream()
                    .mapToDouble(DataPoint::getY).toArray();

                Color color = clusterColors[colorIndex % clusterColors.length];
                scatter.plot(x, y, color, 5.0, "Cluster " + cluster.getKey());
                colorIndex++;
            }

            scatter.setTitle("K-Means Clustering Results");
            scatter.setAxisLabels("Feature 1", "Feature 2");
            scatter.showLegend(true);

            scatter.save("clustering_results.png");
        }
    }
}
```

### **Real-time Streaming Chart**
```java
import com.infinidatum.vizly.streaming.StreamingChart;

@Service
public class IoTMonitoringService {

    private final StreamingChart chart;
    private final List<Double> temperatureData = new ArrayList<>();
    private final List<Double> timestampData = new ArrayList<>();

    @PostConstruct
    public void initializeStreaming() throws VizlyException {
        ChartConfig config = new ChartConfig();
        config.setEnableStreaming(true);
        config.setWidth(1400);
        config.setHeight(600);

        chart = new StreamingChart(config);
        chart.setTitle("Real-time IoT Sensor Monitoring");
        chart.setAxisLabels("Time", "Temperature (°C)");
        chart.showGrid(true);

        // Setup streaming configuration
        StreamingConfig streamConfig = new StreamingConfig();
        streamConfig.setBufferSize(1000);
        streamConfig.setUpdateInterval(0.1); // 10 FPS
        streamConfig.setEnableCompression(true);

        chart.enableStreaming(streamConfig);
    }

    @EventListener
    public void handleSensorData(SensorDataEvent event) throws VizlyException {
        // Add new data point
        timestampData.add((double) System.currentTimeMillis());
        temperatureData.add(event.getTemperature());

        // Keep only last 1000 points for visualization
        if (timestampData.size() > 1000) {
            timestampData.remove(0);
            temperatureData.remove(0);
        }

        // Update streaming chart
        double[] timestamps = timestampData.stream()
            .mapToDouble(Double::doubleValue).toArray();
        double[] temperatures = temperatureData.stream()
            .mapToDouble(Double::doubleValue).toArray();

        chart.updateStreamingData(timestamps, temperatures, 0);

        // Check for anomalies
        if (event.getTemperature() > 80.0) {
            chart.addAnnotation(timestamps[timestamps.length - 1],
                              event.getTemperature(),
                              "HIGH TEMP ALERT", Color.RED);
        }
    }

    @PreDestroy
    public void cleanup() {
        if (chart != null) {
            chart.dispose();
        }
    }
}
```

---

## 🚀 **Spring Boot Integration**

### **Auto-Configuration**
```java
@Configuration
@EnableConfigurationProperties(VizlyProperties.class)
public class VizlyAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public VizlyEngine vizlyEngine(VizlyProperties properties) throws VizlyException {
        VizlyEngine engine = VizlyEngine.getInstance();

        EngineConfig config = new EngineConfig();
        config.setVerbose(properties.isVerbose());
        config.setPythonHome(properties.getPythonHome());
        config.setLogLevel(properties.getLogLevel());

        engine.initialize(config);
        return engine;
    }

    @Bean
    @ConditionalOnMissingBean
    public ChartConfig defaultChartConfig(VizlyProperties properties) {
        ChartConfig config = new ChartConfig();
        config.setWidth(properties.getDefaultWidth());
        config.setHeight(properties.getDefaultHeight());
        config.setEnableGpu(properties.isEnableGpu());
        config.setEnableVr(properties.isEnableVr());
        config.setTheme(properties.getTheme());
        return config;
    }
}

@ConfigurationProperties(prefix = "vizly")
@Data
public class VizlyProperties {
    private boolean verbose = false;
    private String pythonHome = "";
    private String logLevel = "INFO";
    private int defaultWidth = 800;
    private int defaultHeight = 600;
    private boolean enableGpu = false;
    private boolean enableVr = false;
    private String theme = "default";
}
```

### **REST API Integration**
```java
@RestController
@RequestMapping("/api/charts")
public class ChartController {

    private final VizlyEngine engine;
    private final ChartConfig defaultConfig;

    public ChartController(VizlyEngine engine, ChartConfig defaultConfig) {
        this.engine = engine;
        this.defaultConfig = defaultConfig;
    }

    @PostMapping("/line")
    public ResponseEntity<byte[]> createLineChart(@RequestBody ChartDataRequest request) {
        try (LineChart chart = new LineChart(defaultConfig)) {
            chart.plot(request.getX(), request.getY(),
                      Color.fromHex(request.getColor()),
                      request.getLineWidth(),
                      request.getLabel());

            chart.setTitle(request.getTitle());
            chart.setAxisLabels(request.getXLabel(), request.getYLabel());

            String base64Data = chart.exportBase64(300);
            byte[] imageData = Base64.getDecoder().decode(base64Data);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.IMAGE_PNG);
            headers.setContentLength(imageData.length);

            return new ResponseEntity<>(imageData, headers, HttpStatus.OK);

        } catch (VizlyException e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR,
                                           "Chart generation failed", e);
        }
    }

    @GetMapping("/system-info")
    public ResponseEntity<SystemInfo> getSystemInfo() {
        SystemInfo info = engine.getSystemInfo();
        return ResponseEntity.ok(info);
    }

    @PostMapping("/gpu-benchmark")
    public ResponseEntity<BenchmarkResult> runGpuBenchmark(@RequestParam int dataSize) {
        try {
            BenchmarkResult result = performGpuBenchmark(dataSize);
            return ResponseEntity.ok(result);
        } catch (VizlyException e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR,
                                           "Benchmark failed", e);
        }
    }

    private BenchmarkResult performGpuBenchmark(int dataSize) throws VizlyException {
        // Generate test data
        double[] x = IntStream.range(0, dataSize)
            .mapToDouble(i -> i / 1000.0).toArray();
        double[] y = Arrays.stream(x).map(Math::sin).toArray();

        // CPU benchmark
        ChartConfig cpuConfig = new ChartConfig();
        cpuConfig.setEnableGpu(false);

        long cpuStart = System.currentTimeMillis();
        try (LineChart cpuChart = new LineChart(cpuConfig)) {
            cpuChart.plot(x, y);
            cpuChart.save("cpu_benchmark.png");
        }
        long cpuTime = System.currentTimeMillis() - cpuStart;

        // GPU benchmark (if available)
        long gpuTime = cpuTime; // Default to CPU time
        if (engine.isGpuAvailable()) {
            ChartConfig gpuConfig = new ChartConfig();
            gpuConfig.setEnableGpu(true);

            long gpuStart = System.currentTimeMillis();
            try (LineChart gpuChart = new LineChart(gpuConfig)) {
                gpuChart.plot(x, y);
                gpuChart.save("gpu_benchmark.png");
            }
            gpuTime = System.currentTimeMillis() - gpuStart;
        }

        return new BenchmarkResult(dataSize, cpuTime, gpuTime,
                                 (double) cpuTime / gpuTime);
    }
}

@Data
public class ChartDataRequest {
    private double[] x;
    private double[] y;
    private String color = "#0066CC";
    private double lineWidth = 2.0;
    private String label = "";
    private String title = "";
    private String xLabel = "";
    private String yLabel = "";
}

@Data
@AllArgsConstructor
public class BenchmarkResult {
    private int dataSize;
    private long cpuTimeMs;
    private long gpuTimeMs;
    private double speedup;
}
```

---

## 🚀 **Advanced Features**

### **Async Operations with CompletableFuture**
```java
@Service
public class AsyncChartService {

    private final Executor chartExecutor = Executors.newFixedThreadPool(4);

    public CompletableFuture<String> generateMultipleChartsAsync(
            List<DataSet> dataSets) {

        List<CompletableFuture<String>> chartTasks = dataSets.stream()
            .map(this::createChartAsync)
            .collect(Collectors.toList());

        return CompletableFuture.allOf(chartTasks.toArray(new CompletableFuture[0]))
            .thenApply(v -> chartTasks.stream()
                .map(CompletableFuture::join)
                .collect(Collectors.joining(", ")));
    }

    private CompletableFuture<String> createChartAsync(DataSet dataSet) {
        return CompletableFuture.supplyAsync(() -> {
            try (LineChart chart = new LineChart()) {
                chart.plot(dataSet.getX(), dataSet.getY(),
                          dataSet.getColor(), 2.0, dataSet.getName());
                chart.setTitle(dataSet.getName());

                String filename = "chart_" + dataSet.getName() + ".png";
                chart.save(filename);
                return filename;

            } catch (VizlyException e) {
                throw new RuntimeException("Chart generation failed", e);
            }
        }, chartExecutor);
    }
}
```

### **Database Integration with JPA**
```java
@Entity
@Table(name = "chart_data")
public class ChartDataEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "timestamp")
    private LocalDateTime timestamp;

    @Column(name = "value")
    private Double value;

    @Column(name = "series_name")
    private String seriesName;

    // getters and setters...
}

@Repository
public interface ChartDataRepository extends JpaRepository<ChartDataEntity, Long> {
    @Query("SELECT c FROM ChartDataEntity c WHERE c.timestamp BETWEEN :start AND :end ORDER BY c.timestamp")
    List<ChartDataEntity> findByTimestampRange(@Param("start") LocalDateTime start,
                                              @Param("end") LocalDateTime end);

    @Query("SELECT c FROM ChartDataEntity c WHERE c.seriesName = :seriesName ORDER BY c.timestamp DESC")
    List<ChartDataEntity> findLatestBySeries(@Param("seriesName") String seriesName,
                                           Pageable pageable);
}

@Service
@Transactional
public class DatabaseChartService {

    private final ChartDataRepository repository;
    private final ChartConfig config;

    public DatabaseChartService(ChartDataRepository repository, ChartConfig config) {
        this.repository = repository;
        this.config = config;
    }

    public byte[] createTimeSeriesChart(String seriesName,
                                       LocalDateTime start,
                                       LocalDateTime end) throws VizlyException {

        List<ChartDataEntity> data = repository.findByTimestampRange(start, end);

        if (data.isEmpty()) {
            throw new IllegalArgumentException("No data found for the specified range");
        }

        // Convert to arrays
        double[] timestamps = data.stream()
            .mapToDouble(entity -> entity.getTimestamp()
                .toEpochSecond(ZoneOffset.UTC))
            .toArray();

        double[] values = data.stream()
            .mapToDouble(ChartDataEntity::getValue)
            .toArray();

        try (LineChart chart = new LineChart(config)) {
            chart.plot(timestamps, values, Color.BLUE, 2.0, seriesName);
            chart.setTitle("Time Series: " + seriesName);
            chart.setAxisLabels("Time", "Value");
            chart.showGrid(true);

            String base64Data = chart.exportBase64(300);
            return Base64.getDecoder().decode(base64Data);
        }
    }
}
```

### **Microservices Architecture**
```java
@Configuration
@EnableEurekaClient
public class MicroserviceConfig {

    @Bean
    @LoadBalanced
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}

@FeignClient(name = "chart-service", fallback = ChartServiceFallback.class)
public interface ChartServiceClient {

    @PostMapping("/api/charts/line")
    ResponseEntity<byte[]> createLineChart(@RequestBody ChartDataRequest request);

    @GetMapping("/api/charts/system-info")
    ResponseEntity<SystemInfo> getSystemInfo();
}

@Component
public class ChartServiceFallback implements ChartServiceClient {

    @Override
    public ResponseEntity<byte[]> createLineChart(ChartDataRequest request) {
        // Fallback implementation - perhaps a static chart or error image
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).build();
    }

    @Override
    public ResponseEntity<SystemInfo> getSystemInfo() {
        SystemInfo fallbackInfo = new SystemInfo();
        fallbackInfo.setVersion("unknown");
        fallbackInfo.setGpuAvailable(false);
        return ResponseEntity.ok(fallbackInfo);
    }
}
```

---

## 🛠️ **Build System Integration**

### **Maven Configuration**
```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>vizly-app</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <spring-boot.version>3.2.0</spring-boot.version>
        <vizly.version>1.0.0</vizly.version>
    </properties>

    <dependencies>
        <!-- Vizly SDK -->
        <dependency>
            <groupId>com.infinidatum</groupId>
            <artifactId>vizly-sdk</artifactId>
            <version>${vizly.version}</version>
        </dependency>

        <!-- Spring Boot -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>${spring-boot.version}</version>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
            <version>${spring-boot.version}</version>
        </dependency>

        <!-- Database -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <version>${spring-boot.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <version>${spring-boot.version}</version>
            </plugin>

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.0.0-M9</version>
                <configuration>
                    <systemPropertyVariables>
                        <java.library.path>${project.basedir}/native-libs</java.library.path>
                    </systemPropertyVariables>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### **Gradle Configuration**
```gradle
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
    id 'io.spring.dependency-management' version '1.1.0'
}

group = 'com.example'
version = '1.0.0'
sourceCompatibility = '11'

repositories {
    mavenCentral()
    maven {
        url 'https://repo.infinidatum.com/maven-public'
        credentials {
            username = project.findProperty('infinidatum.username')
            password = project.findProperty('infinidatum.password')
        }
    }
}

dependencies {
    // Vizly SDK
    implementation 'com.infinidatum:vizly-sdk:1.0.0'

    // Spring Boot
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'

    // Database
    runtimeOnly 'com.h2database:h2'

    // Testing
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.testcontainers:junit-jupiter'
}

test {
    useJUnitPlatform()
    systemProperty 'java.library.path', "${projectDir}/native-libs"
}

// Docker image build
docker {
    name = "${project.group}/${project.name}:${project.version}"
    files jar.archiveFile.get()
    buildArgs(['JAR_FILE': "${jar.archiveFileName.get()}"])
}
```

---

## 📚 **API Reference**

### **Core Classes**
```java
// Engine management
public class VizlyEngine {
    public static VizlyEngine getInstance();
    public void initialize(EngineConfig config) throws VizlyException;
    public void initialize() throws VizlyException;
    public SystemInfo getSystemInfo();
    public boolean isGpuAvailable();
    public boolean isVrAvailable();
    public boolean isStreamingAvailable();
    public void shutdown();
}

// Chart base class
public abstract class VizlyChart implements AutoCloseable {
    public abstract void setTitle(String title) throws VizlyException;
    public abstract void setAxisLabels(String xLabel, String yLabel) throws VizlyException;
    public abstract void showGrid(boolean show) throws VizlyException;
    public abstract void showLegend(boolean show) throws VizlyException;
    public abstract void save(String filename) throws VizlyException;
    public abstract String exportBase64(int dpi) throws VizlyException;
    public abstract void dispose();
}

// Line chart implementation
public class LineChart extends VizlyChart {
    public LineChart(ChartConfig config) throws VizlyException;
    public LineChart() throws VizlyException;

    public void plot(double[] x, double[] y) throws VizlyException;
    public void plot(double[] x, double[] y, Color color) throws VizlyException;
    public void plot(double[] x, double[] y, Color color, double lineWidth, String label) throws VizlyException;
    public void plotMultiple(List<LineSeriesData> seriesData) throws VizlyException;

    public void addTrendLine(double[] x, double[] y, String type, Color color) throws VizlyException;
    public void addVerticalLine(double x, Color color, double lineWidth, String label) throws VizlyException;
    public void addHorizontalLine(double y, Color color, double lineWidth, String label) throws VizlyException;
    public void setLimits(double xMin, double xMax, double yMin, double yMax) throws VizlyException;
    public void setLogScale(boolean xLog, boolean yLog) throws VizlyException;
    public void addAnnotation(double x, double y, String text, Color color) throws VizlyException;

    public CompletableFuture<Void> saveAsync(String filename);
    public int getSeriesCount();
}
```

### **Configuration Classes**
```java
public class ChartConfig {
    private int width = 800;
    private int height = 600;
    private String backgroundColor = "white";
    private boolean enableGpu = false;
    private boolean enableVr = false;
    private boolean enableStreaming = false;
    private String theme = "default";

    // getters and setters...
}

public class SystemInfo {
    private String version;
    private boolean gpuAvailable;
    private boolean vrAvailable;
    private boolean streamingAvailable;
    private String platform;
    private String pythonVersion;

    // getters and setters...
}

public class Color {
    public static final Color RED = new Color(1.0, 0.0, 0.0);
    public static final Color GREEN = new Color(0.0, 1.0, 0.0);
    public static final Color BLUE = new Color(0.0, 0.0, 1.0);
    // ... other predefined colors

    public static Color fromHex(String hex);
    public static Color fromRgb(int r, int g, int b);
    public String toHex();
}
```

---

## 🧪 **Testing**

### **Unit Testing with JUnit 5**
```java
@ExtendWith(MockitoExtension.class)
class LineChartTest {

    private VizlyEngine engine;
    private ChartConfig config;

    @BeforeEach
    void setUp() throws VizlyException {
        engine = VizlyEngine.getInstance();
        engine.initialize();

        config = new ChartConfig();
        config.setWidth(400);
        config.setHeight(300);
    }

    @AfterEach
    void tearDown() {
        engine.shutdown();
    }

    @Test
    void testBasicLinePlot() throws VizlyException {
        try (LineChart chart = new LineChart(config)) {
            double[] x = {1, 2, 3, 4, 5};
            double[] y = {2, 4, 6, 8, 10};

            assertDoesNotThrow(() -> chart.plot(x, y));
            assertEquals(1, chart.getSeriesCount());
        }
    }

    @Test
    void testInvalidDataThrowsException() {
        try (LineChart chart = new LineChart(config)) {
            double[] x = {1, 2, 3};
            double[] y = {1, 2}; // Different length

            assertThrows(VizlyException.class, () -> chart.plot(x, y));
        }
    }

    @Test
    void testAsyncSaveOperation() throws VizlyException {
        try (LineChart chart = new LineChart(config)) {
            double[] x = {1, 2, 3, 4, 5};
            double[] y = {1, 4, 9, 16, 25};

            chart.plot(x, y);

            CompletableFuture<Void> future = chart.saveAsync("test_async.png");
            assertDoesNotThrow(() -> future.get(5, TimeUnit.SECONDS));
        }
    }

    @Test
    @EnabledIf("isGpuAvailable")
    void testGpuAcceleration() throws VizlyException {
        config.setEnableGpu(true);

        try (LineChart chart = new LineChart(config)) {
            // Large dataset for GPU test
            double[] x = IntStream.range(0, 10000).mapToDouble(i -> i).toArray();
            double[] y = Arrays.stream(x).map(Math::sin).toArray();

            long start = System.currentTimeMillis();
            chart.plot(x, y);
            chart.save("gpu_test.png");
            long duration = System.currentTimeMillis() - start;

            // GPU should be faster for large datasets
            assertTrue(duration < 5000, "GPU rendering should complete within 5 seconds");
        }
    }

    static boolean isGpuAvailable() {
        try {
            return VizlyEngine.getInstance().isGpuAvailable();
        } catch (Exception e) {
            return false;
        }
    }
}
```

### **Integration Testing with Spring Boot**
```java
@SpringBootTest
@TestMethodOrder(OrderAnnotation.class)
class ChartControllerIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private ChartController chartController;

    @Test
    @Order(1)
    void testSystemInfo() {
        ResponseEntity<SystemInfo> response = restTemplate.getForEntity(
            "/api/charts/system-info", SystemInfo.class);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertNotNull(response.getBody().getVersion());
    }

    @Test
    @Order(2)
    void testLineChartCreation() {
        ChartDataRequest request = new ChartDataRequest();
        request.setX(new double[]{1, 2, 3, 4, 5});
        request.setY(new double[]{2, 4, 6, 8, 10});
        request.setTitle("Integration Test Chart");
        request.setColor("#FF5733");

        ResponseEntity<byte[]> response = restTemplate.postForEntity(
            "/api/charts/line", request, byte[].class);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertTrue(response.getBody().length > 0);
        assertEquals(MediaType.IMAGE_PNG, response.getHeaders().getContentType());
    }

    @Test
    @Order(3)
    void testInvalidDataReturnsError() {
        ChartDataRequest request = new ChartDataRequest();
        request.setX(new double[]{1, 2, 3});
        request.setY(new double[]{1, 2}); // Invalid - different lengths

        ResponseEntity<String> response = restTemplate.postForEntity(
            "/api/charts/line", request, String.class);

        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, response.getStatusCode());
    }
}
```

---

## 💼 **Enterprise Features**

### **Commercial Licensing**
- **Professional Support**: Java expertise and Spring Boot integration
- **Enterprise Support**: 24/7 support with dedicated Java specialists
- **Custom Development**: Tailored Java components and integrations
- **Architecture Consulting**: Microservices and cloud deployment guidance

### **Security & Compliance**
- **Data Privacy**: All processing occurs within your Java application
- **Authentication**: Integration with Spring Security, OAuth2, JWT
- **Audit Logging**: Comprehensive operation tracking and compliance
- **Encryption**: Support for data encryption at rest and in transit

### **Performance & Scalability**
- **Connection Pooling**: Efficient Python process management
- **Load Balancing**: Multi-instance chart generation
- **Caching**: Intelligent chart caching with Redis/Hazelcast
- **Monitoring**: Integration with Micrometer, Prometheus, Grafana

### **Cloud & Container Support**
- **Docker**: Optimized container images
- **Kubernetes**: Helm charts and deployment manifests
- **Cloud Platforms**: AWS, Azure, GCP deployment guides
- **CI/CD**: Jenkins, GitHub Actions, GitLab CI templates

---

## 📞 **Support & Resources**

### **Documentation**
- **API Javadocs**: Complete method documentation
- **Spring Boot Guide**: Integration best practices
- **Performance Tuning**: JVM and application optimization
- **Cloud Deployment**: Container and cloud deployment guides

### **Community & Support**
- **Email**: durai@infinidatum.net
- **Subject Line**: "Java SDK Support Request"
- **Include**: Java version, Spring Boot version, application logs

### **Professional Services**
- **Architecture Review**: Java application design consultation
- **Performance Optimization**: JVM tuning and application optimization
- **Training**: Enterprise Java SDK training program
- **Migration**: Migration from other charting libraries

---

## 🚀 **Getting Started Checklist**

- [ ] Install Java 11 or later
- [ ] Install Python 3.8+ with development headers
- [ ] Add Vizly SDK Maven/Gradle dependency
- [ ] Initialize VizlyEngine in your application
- [ ] Create and test basic LineChart
- [ ] Test GPU acceleration (if available)
- [ ] Integrate with Spring Boot (if applicable)
- [ ] Set up proper resource management (try-with-resources)
- [ ] Contact for enterprise licensing if needed

### **Next Steps**
1. **Evaluate**: Test with your Java application requirements
2. **Integrate**: Add to your existing Spring Boot applications
3. **Scale**: Deploy to production microservices architecture
4. **Monitor**: Set up monitoring and alerting
5. **Support**: Contact for enterprise features and consulting

---

**☕ Transform your Java applications with enterprise-grade visualization capabilities.**

**Contact durai@infinidatum.net for enterprise licensing and Java consulting services.**

---

*© 2024 Infinidatum Corporation. All rights reserved. Commercial license required for enterprise use.*