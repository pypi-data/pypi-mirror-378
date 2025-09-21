/*
 * Copyright (c) 2024 Infinidatum Corporation. All rights reserved.
 * Commercial License - Contact durai@infinidatum.net
 */

package com.infinidatum.vizly.core;

import com.infinidatum.vizly.exceptions.VizlyException;
import com.infinidatum.vizly.types.EngineConfig;
import com.infinidatum.vizly.types.SystemInfo;

import jep.Jep;
import jep.JepConfig;
import jep.JepException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.locks.ReentrantLock;

/**
 * Main engine class for Vizly Java SDK
 *
 * @author Infinidatum Corporation
 * @version 1.0.0
 * @since 1.0.0
 */
public class VizlyEngine {

    private static final Logger logger = LoggerFactory.getLogger(VizlyEngine.class);
    private static final ReentrantLock lock = new ReentrantLock();
    private static VizlyEngine instance;
    private static boolean initialized = false;

    private Jep jep;
    private EngineConfig config;
    private SystemInfo systemInfo;

    /**
     * Private constructor - use getInstance()
     */
    private VizlyEngine() {
        // Private constructor for singleton
    }

    /**
     * Get singleton instance of VizlyEngine
     *
     * @return VizlyEngine instance
     */
    public static VizlyEngine getInstance() {
        if (instance == null) {
            lock.lock();
            try {
                if (instance == null) {
                    instance = new VizlyEngine();
                }
            } finally {
                lock.unlock();
            }
        }
        return instance;
    }

    /**
     * Initialize the Vizly engine
     *
     * @param config Engine configuration
     * @throws VizlyException if initialization fails
     */
    public void initialize(EngineConfig config) throws VizlyException {
        lock.lock();
        try {
            if (initialized) {
                logger.warn("VizlyEngine already initialized");
                return;
            }

            this.config = config;
            logger.info("🚀 Initializing Vizly Java SDK v1.0.0");

            // Setup JEP configuration
            JepConfig jepConfig = new JepConfig();
            if (config.getPythonHome() != null && !config.getPythonHome().isEmpty()) {
                jepConfig.setPythonHome(config.getPythonHome());
            }

            // Create JEP instance
            try {
                jep = new Jep(jepConfig);

                // Import Vizly
                jep.eval("import vizly");
                jep.eval("import numpy as np");

                logger.info("✅ Python environment initialized");

                // Check Vizly installation
                String version = (String) jep.getValue("vizly.__version__");
                logger.info("📦 Vizly version: {}", version);

                // Get system information
                loadSystemInfo();

                initialized = true;
                logger.info("🎉 Vizly engine initialized successfully");

            } catch (JepException e) {
                throw new VizlyException("Failed to initialize Python environment: " + e.getMessage(), e);
            }

        } finally {
            lock.unlock();
        }
    }

    /**
     * Initialize with default configuration
     *
     * @throws VizlyException if initialization fails
     */
    public void initialize() throws VizlyException {
        initialize(new EngineConfig());
    }

    /**
     * Load system information from Vizly
     */
    private void loadSystemInfo() throws VizlyException {
        try {
            String version = (String) jep.getValue("vizly.__version__");

            // Check feature availability
            boolean gpuAvailable = false;
            boolean vrAvailable = false;
            boolean streamingAvailable = false;

            try {
                jep.eval("import vizly.gpu");
                gpuAvailable = true;
                logger.debug("🚀 GPU acceleration available");
            } catch (JepException e) {
                logger.debug("📋 GPU acceleration not available");
            }

            try {
                jep.eval("import vizly.vr");
                vrAvailable = true;
                logger.debug("🥽 VR/AR features available");
            } catch (JepException e) {
                logger.debug("📋 VR/AR features not available");
            }

            try {
                jep.eval("import vizly.streaming");
                streamingAvailable = true;
                logger.debug("📡 Streaming features available");
            } catch (JepException e) {
                logger.debug("📋 Streaming features not available");
            }

            // Get platform info
            String platform = (String) jep.getValue("vizly.get_platform()");
            String pythonVersion = (String) jep.getValue("vizly.get_python_version()");

            systemInfo = new SystemInfo(version, gpuAvailable, vrAvailable,
                                      streamingAvailable, platform, pythonVersion);

        } catch (JepException e) {
            throw new VizlyException("Failed to load system information: " + e.getMessage(), e);
        }
    }

    /**
     * Get system information
     *
     * @return SystemInfo object
     */
    public SystemInfo getSystemInfo() {
        return systemInfo;
    }

    /**
     * Check if GPU acceleration is available
     *
     * @return true if GPU is available
     */
    public boolean isGpuAvailable() {
        return systemInfo != null && systemInfo.isGpuAvailable();
    }

    /**
     * Check if VR/AR features are available
     *
     * @return true if VR/AR is available
     */
    public boolean isVrAvailable() {
        return systemInfo != null && systemInfo.isVrAvailable();
    }

    /**
     * Check if streaming features are available
     *
     * @return true if streaming is available
     */
    public boolean isStreamingAvailable() {
        return systemInfo != null && systemInfo.isStreamingAvailable();
    }

    /**
     * Get JEP instance for direct Python interaction
     *
     * @return JEP instance
     * @throws VizlyException if engine not initialized
     */
    public Jep getJep() throws VizlyException {
        if (!initialized || jep == null) {
            throw new VizlyException("VizlyEngine not initialized. Call initialize() first.");
        }
        return jep;
    }

    /**
     * Execute Python code
     *
     * @param code Python code to execute
     * @throws VizlyException if execution fails
     */
    public void eval(String code) throws VizlyException {
        try {
            jep.eval(code);
        } catch (JepException e) {
            throw new VizlyException("Python execution failed: " + e.getMessage(), e);
        }
    }

    /**
     * Get Python variable value
     *
     * @param variable Variable name
     * @return Variable value
     * @throws VizlyException if retrieval fails
     */
    public Object getValue(String variable) throws VizlyException {
        try {
            return jep.getValue(variable);
        } catch (JepException e) {
            throw new VizlyException("Failed to get Python variable: " + e.getMessage(), e);
        }
    }

    /**
     * Set Python variable value
     *
     * @param variable Variable name
     * @param value Variable value
     * @throws VizlyException if setting fails
     */
    public void setValue(String variable, Object value) throws VizlyException {
        try {
            jep.set(variable, value);
        } catch (JepException e) {
            throw new VizlyException("Failed to set Python variable: " + e.getMessage(), e);
        }
    }

    /**
     * Check if engine is initialized
     *
     * @return true if initialized
     */
    public boolean isInitialized() {
        return initialized;
    }

    /**
     * Get engine configuration
     *
     * @return EngineConfig
     */
    public EngineConfig getConfig() {
        return config;
    }

    /**
     * Shutdown the engine
     */
    public void shutdown() {
        lock.lock();
        try {
            if (initialized && jep != null) {
                try {
                    jep.close();
                    logger.info("🔄 Vizly engine shutdown complete");
                } catch (JepException e) {
                    logger.error("Error during shutdown: {}", e.getMessage());
                }
                jep = null;
                initialized = false;
            }
        } finally {
            lock.unlock();
        }
    }

    /**
     * Finalize - ensure cleanup
     */
    @Override
    protected void finalize() throws Throwable {
        shutdown();
        super.finalize();
    }
}