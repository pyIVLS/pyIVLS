import matplotlib.pyplot as plt
import numpy as np
import os
import sys

def read_iv_data_from_file(filepath):
    """
    Read I-V data from a .dat file.
    Returns current and voltage arrays.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    current = []
    voltage = []
    
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Skip header lines that don't contain numeric data
            if line.startswith('IS_4pr') or line.startswith('VS_4pr'):
                continue
                
            # Try to parse the line as two comma-separated numbers
            try:
                parts = line.split(',')
                if len(parts) == 2:
                    curr = float(parts[0])
                    volt = float(parts[1])
                    current.append(curr)
                    voltage.append(volt)
            except ValueError:
                # Skip lines that can't be parsed as numbers
                continue
    
    return np.array(current), np.array(voltage)

# Data file path - can be overridden by command line argument
datapath = "plugins/sweep-1.0.0/406-CTLM-FLAT_iter2_c.dat"

# Check if a file path was provided as command line argument
if len(sys.argv) > 1:
    datapath = sys.argv[1]
    print(f"Using data file from command line: {datapath}")

# Read data from file
try:
    current, voltage = read_iv_data_from_file(datapath)
    print(f"Successfully loaded data from: {datapath}")
    print(f"Number of data points: {len(current)}")
    
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Using hardcoded data instead...")
    
    # Fallback to hardcoded data if file not found
    data = [
    (-2.092988602817e-02, -9.998595714569e-01),
    (-2.289977110922e-02, -9.800410270691e-01),
    (-2.201031520963e-02, -9.600052833557e-01),
    (-2.211905829608e-02, -9.400525093079e-01),
    (-2.077850140631e-02, -9.200208187103e-01),
    (-2.069994248450e-02, -9.000296592712e-01),
    (-1.928536966443e-02, -8.800287246704e-01),
    (-1.913464069366e-02, -8.600351810455e-01),
    (-1.777089945972e-02, -8.400139808655e-01),
    (-1.761159859598e-02, -8.200559616089e-01),
    (-1.626696623862e-02, -8.000257015228e-01),
    (-1.610924117267e-02, -7.800259590149e-01),
    (-1.483474951237e-02, -7.599933147430e-01),
    (-1.464425306767e-02, -7.400431632996e-01),
    (-1.343246735632e-02, -7.200045585632e-01),
    (-1.325482130051e-02, -7.000193595886e-01),
    (-1.210060156882e-02, -6.800239086151e-01),
    (-1.189149636775e-02, -6.600484848022e-01),
    (-1.082418020815e-02, -6.399972438812e-01),
    (-1.059904135764e-02, -6.200411319733e-01),
    (-9.987687692046e-03, -6.000223159790e-01),
    (-9.129120036960e-03, -5.800006389618e-01),
    (-8.779246360064e-03, -5.600466728210e-01),
    (-7.926703430712e-03, -5.400176048279e-01),
    (-7.556359749287e-03, -5.200281143188e-01),
    (-6.725622341037e-03, -5.000326633453e-01),
    (-6.313830614090e-03, -4.800312519074e-01),
    (-5.549298599362e-03, -4.600136280060e-01),
    (-5.116769112647e-03, -4.400525093079e-01),
    (-4.369891714305e-03, -4.200294017792e-01),
    (-3.930325619876e-03, -4.000334739685e-01),
    (-3.238645615056e-03, -3.800036907196e-01),
    (-2.761081326753e-03, -3.600435256958e-01),
    (-2.118487376720e-03, -3.400173187256e-01),
    (-1.651632715948e-03, -3.200180530548e-01),
    (-1.066306838766e-03, -3.000304698944e-01),
    (-3.843597005471e-05, -2.800045013428e-01),
    (-2.297904393345e-05, -2.600147724152e-01),
    (-3.477030986687e-05, -2.400338649750e-01),
    (-2.118068778145e-06, -2.200183868408e-01),
    (-1.503245812273e-06, -1.999916583300e-01),
    (-1.405538341714e-06, -1.799820661545e-01),
    (-1.589764337950e-06, -1.599899083376e-01),
    (-1.458759243178e-06, -1.400005668402e-01),
    (-2.080947069771e-06, -1.199978366494e-01),
    (-2.153592049581e-06, -9.999208897352e-02),
    (-2.279802401972e-06, -8.000202476978e-02),
    (-1.911039362312e-06, -6.001551076770e-02),
    (-1.214452936438e-06, -4.001808166504e-02),
    (-2.801141590680e-06, -1.999974250794e-02),
    (-2.799733692882e-06, 1.387596148561e-05),
    (-2.203868461947e-06, 2.000122144818e-02),
    (-1.509399339739e-06, 4.000680521131e-02),
    (-1.294504386351e-06, 6.002230569720e-02),
    (-1.465110699428e-06, 8.001983165741e-02),
    (-1.431769078408e-06, 1.000101342797e-01),
    (-2.006744125538e-06, 1.200144290924e-01),
    (-1.983183665288e-06, 1.400290727615e-01),
    (-2.132673216693e-06, 1.600201576948e-01),
    (-1.888517090265e-06, 1.800057142973e-01),
    (-1.219905584549e-06, 2.000021487474e-01),
    (-2.623600948937e-06, 2.199542522430e-01),
    (-2.703642849156e-06, 2.399299144745e-01),
    (-2.223497631348e-06, 2.599320411682e-01),
    (-1.489893179496e-06, 2.799520492554e-01),
    (-1.134091576205e-06, 2.999374866486e-01),
    (-1.261874444936e-06, 3.199529647827e-01),
    (-1.316729708378e-06, 3.399567604065e-01),
    (-1.870367441370e-06, 3.599314689636e-01),
    (-1.715025859994e-06, 3.799581527710e-01),
    (-1.871893346106e-06, 3.999671936035e-01),
    (-1.751713739395e-06, 4.199306964874e-01),
    (-1.144511657003e-06, 4.399333000183e-01),
    (-2.273092150062e-06, 4.599695205688e-01),
    (-2.410389015495e-06, 4.799454212189e-01),
    (-2.068768708341e-06, 4.999344348908e-01),
    (-1.357473138341e-06, 5.199489593506e-01),
    (-2.766573288682e-06, 5.399415493012e-01),
    (-2.794120291583e-06, 5.599486827850e-01),
    (-2.254122364320e-06, 5.799365043640e-01),
    (-1.532928877168e-06, 5.999233722687e-01),
    (-1.236515004166e-06, 6.199460029602e-01),
    (-1.387585371049e-06, 6.399624347687e-01),
    (-1.411423681930e-06, 6.599254608154e-01),
    (-1.944748191818e-06, 6.799416542053e-01),
    (-1.839132210080e-06, 6.999616622925e-01),
    (-1.994017338802e-06, 7.199358940124e-01),
    (-1.825972731240e-06, 7.399420738220e-01),
    (-1.194323317577e-06, 7.599403858185e-01),
    (-2.426556193313e-06, 7.799494266510e-01),
    (-2.555640776336e-06, 7.999539375305e-01),
    (-2.178820295740e-06, 8.199534416199e-01),
    (-1.465375362386e-06, 8.399255275726e-01),
    (-1.025543156175e-06, 8.599483966827e-01),
    (-1.113270513997e-06, 8.799667358398e-01),
    (-1.246699071089e-06, 8.999376296997e-01),
    (-1.925517381096e-06, 9.199376106262e-01),
    (-1.697462721495e-06, 9.399714469910e-01),
    (-1.852462219176e-06, 9.599459171295e-01),
    (-1.816650637920e-06, 9.799611568451e-01),
    (-1.271123892366e-06, 9.999635219574e-01),
    ]
    
    # Extract current and voltage arrays from hardcoded data
    current = np.array([point[0] for point in data])  # Current in Amperes
    voltage = np.array([point[1] for point in data])  # Voltage in Volts

# Create I-V characteristic plot (I on Y-axis, V on X-axis)
plt.figure(figsize=(12, 8))
plt.plot(voltage, current, 'b-o', markersize=2, linewidth=1.5, label='I-V Characteristic')
plt.xlabel('Voltage (V)', fontsize=12)
plt.ylabel('Current (A)', fontsize=12)
plt.title(f'Current-Voltage (I-V) Characteristic\nData source: {datapath}', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=11)

# Add some styling
plt.tight_layout()

# Display basic statistics
print(f"\nData Summary:")
print(f"Number of data points: {len(current)}")
print(f"Voltage range: {voltage.min():.3f} V to {voltage.max():.3f} V")
print(f"Current range: {current.min():.6f} A to {current.max():.6f} A")
print(f"Maximum current magnitude: {abs(current).max():.6f} A")

# Calculate and display resistance (if meaningful)
if len(current) > 0 and not np.allclose(current, 0):
    # Find points near zero voltage for resistance calculation
    zero_v_idx = np.argmin(np.abs(voltage))
    if abs(voltage[zero_v_idx]) < 0.1 and abs(current[zero_v_idx]) > 1e-9:
        resistance = voltage[zero_v_idx] / current[zero_v_idx]
        print(f"Approximate resistance near V=0: {resistance:.2f} Ω")

# Show the plot
plt.show()