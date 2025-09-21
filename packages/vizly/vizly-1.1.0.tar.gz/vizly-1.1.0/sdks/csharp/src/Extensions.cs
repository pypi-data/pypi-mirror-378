using System;
using System.Linq;
using Python.Runtime;

namespace Vizly.SDK
{
    /// <summary>
    /// Extension methods for .NET to Python interop
    /// </summary>
    public static class Extensions
    {
        /// <summary>
        /// Convert .NET array to NumPy array
        /// </summary>
        public static PyObject ToNumpyArray(this double[] array)
        {
            using (Py.GIL())
            {
                dynamic np = Py.Import("numpy");
                return np.array(array);
            }
        }

        /// <summary>
        /// Convert .NET array to NumPy array
        /// </summary>
        public static PyObject ToNumpyArray(this float[] array)
        {
            using (Py.GIL())
            {
                dynamic np = Py.Import("numpy");
                return np.array(array);
            }
        }

        /// <summary>
        /// Convert .NET array to NumPy array
        /// </summary>
        public static PyObject ToNumpyArray(this int[] array)
        {
            using (Py.GIL())
            {
                dynamic np = Py.Import("numpy");
                return np.array(array);
            }
        }

        /// <summary>
        /// Convert .NET 2D array to NumPy array
        /// </summary>
        public static PyObject ToNumpyArray(this double[,] array)
        {
            using (Py.GIL())
            {
                dynamic np = Py.Import("numpy");

                int rows = array.GetLength(0);
                int cols = array.GetLength(1);

                var flatArray = new double[rows * cols];
                for (int i = 0; i < rows; i++)
                {
                    for (int j = 0; j < cols; j++)
                    {
                        flatArray[i * cols + j] = array[i, j];
                    }
                }

                var npArray = np.array(flatArray);
                return npArray.reshape(rows, cols);
            }
        }

        /// <summary>
        /// Convert string array to Python list
        /// </summary>
        public static PyList ToPythonList(this string[] array)
        {
            using (Py.GIL())
            {
                var list = new PyList();
                foreach (var item in array)
                {
                    list.Append(item.ToPython());
                }
                return list;
            }
        }

        /// <summary>
        /// Convert NumPy array to .NET array
        /// </summary>
        public static double[] ToDoubleArray(this PyObject npArray)
        {
            using (Py.GIL())
            {
                dynamic array = npArray;
                var list = array.tolist();
                return list.As<double[]>();
            }
        }

        /// <summary>
        /// Check if Vizly GPU is available
        /// </summary>
        public static bool IsGpuAvailable()
        {
            try
            {
                using (Py.GIL())
                {
                    dynamic vizly = Py.Import("vizly");
                    dynamic gpu = vizly.gpu;
                    return gpu.is_available().As<bool>();
                }
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Check if Vizly VR is available
        /// </summary>
        public static bool IsVrAvailable()
        {
            try
            {
                using (Py.GIL())
                {
                    dynamic vizly = Py.Import("vizly");
                    dynamic vr = vizly.vr;
                    return vr.is_available().As<bool>();
                }
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Get Vizly version
        /// </summary>
        public static string GetVizlyVersion()
        {
            using (Py.GIL())
            {
                dynamic vizly = Py.Import("vizly");
                return vizly.__version__.As<string>();
            }
        }

        /// <summary>
        /// Get system information for Vizly
        /// </summary>
        public static VizlySystemInfo GetSystemInfo()
        {
            using (Py.GIL())
            {
                dynamic vizly = Py.Import("vizly");
                var info = vizly.get_system_info();

                return new VizlySystemInfo
                {
                    Version = info["version"].As<string>(),
                    GpuAvailable = info["gpu_available"].As<bool>(),
                    VrAvailable = info["vr_available"].As<bool>(),
                    StreamingAvailable = info["streaming_available"].As<bool>(),
                    Platform = info["platform"].As<string>(),
                    PythonVersion = info["python_version"].As<string>()
                };
            }
        }
    }

    /// <summary>
    /// System information for Vizly
    /// </summary>
    public class VizlySystemInfo
    {
        public string Version { get; set; } = "";
        public bool GpuAvailable { get; set; }
        public bool VrAvailable { get; set; }
        public bool StreamingAvailable { get; set; }
        public string Platform { get; set; } = "";
        public string PythonVersion { get; set; } = "";

        public override string ToString()
        {
            return $"Vizly {Version} on {Platform} (Python {PythonVersion}) - " +
                   $"GPU: {GpuAvailable}, VR: {VrAvailable}, Streaming: {StreamingAvailable}";
        }
    }
}