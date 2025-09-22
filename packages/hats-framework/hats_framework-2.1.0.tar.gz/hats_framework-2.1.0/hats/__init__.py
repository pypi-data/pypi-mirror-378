"""
HATS - Hacking Automation Tool Suite
A flexible framework for cybersecurity automation.
"""

__version__ = "2.0.0"
__author__ = "HATS Team"

from .core import HATSEngine, ToolResult
from .tool_manager import ToolManager
from .config_loader import ConfigLoader
from .dynamic_interface import (
    HATS, 
    DynamicToolInterface,
    ReconTools,
    ExploitTools, 
    PostExploitTools
)
from .security import ArgumentSanitizer

# Create global instances for easy access
_hats_instance = None

def get_hats_instance():
    """Get or create global HATS instance."""
    global _hats_instance
    if _hats_instance is None:
        _hats_instance = HATS()
    return _hats_instance

# Simple function interface (like your example)
def nmap(*args, **kwargs):
    """Execute nmap with intelligent argument detection."""
    return get_hats_instance().nmap(*args, **kwargs)

def masscan(*args, **kwargs):
    """Execute masscan with intelligent argument detection."""
    return get_hats_instance().masscan(*args, **kwargs)

def rustscan(*args, **kwargs):
    """Execute rustscan with intelligent argument detection."""
    return get_hats_instance().rustscan(*args, **kwargs)

def zmap(*args, **kwargs):
    """Execute zmap with intelligent argument detection."""
    return get_hats_instance().zmap(*args, **kwargs)

def nikto(*args, **kwargs):
    """Execute nikto with intelligent argument detection."""
    return get_hats_instance().nikto(*args, **kwargs)

def gobuster(*args, **kwargs):
    """Execute gobuster with intelligent argument detection."""
    return get_hats_instance().gobuster(*args, **kwargs)

def dirb(*args, **kwargs):
    """Execute dirb with intelligent argument detection."""
    return get_hats_instance().dirb(*args, **kwargs)

def whatweb(*args, **kwargs):
    """Execute whatweb with intelligent argument detection."""
    return get_hats_instance().whatweb(*args, **kwargs)

def wfuzz(*args, **kwargs):
    """Execute wfuzz with intelligent argument detection."""
    return get_hats_instance().wfuzz(*args, **kwargs)

def ffuf(*args, **kwargs):
    """Execute ffuf with intelligent argument detection."""
    return get_hats_instance().ffuf(*args, **kwargs)

def nuclei(*args, **kwargs):
    """Execute nuclei with intelligent argument detection."""
    return get_hats_instance().nuclei(*args, **kwargs)

def hydra(*args, **kwargs):
    """Execute hydra with intelligent argument detection."""
    return get_hats_instance().hydra(*args, **kwargs)

def medusa(*args, **kwargs):
    """Execute medusa with intelligent argument detection."""
    return get_hats_instance().medusa(*args, **kwargs)

def ncrack(*args, **kwargs):
    """Execute ncrack with intelligent argument detection."""
    return get_hats_instance().ncrack(*args, **kwargs)

def sqlmap(*args, **kwargs):
    """Execute sqlmap with intelligent argument detection."""
    return get_hats_instance().sqlmap(*args, **kwargs)

def john(*args, **kwargs):
    """Execute john with intelligent argument detection."""
    return get_hats_instance().john(*args, **kwargs)

def hashcat(*args, **kwargs):
    """Execute hashcat with intelligent argument detection."""
    return get_hats_instance().hashcat(*args, **kwargs)

def crunch(*args, **kwargs):
    """Execute crunch with intelligent argument detection."""
    return get_hats_instance().crunch(*args, **kwargs)

def cewl(*args, **kwargs):
    """Execute cewl with intelligent argument detection."""
    return get_hats_instance().cewl(*args, **kwargs)

def aircrack(*args, **kwargs):
    """Execute aircrack-ng with intelligent argument detection."""
    return get_hats_instance().aircrack(*args, **kwargs)

def airodump(*args, **kwargs):
    """Execute airodump-ng with intelligent argument detection."""
    return get_hats_instance().airodump(*args, **kwargs)

def reaver(*args, **kwargs):
    """Execute reaver with intelligent argument detection."""
    return get_hats_instance().reaver(*args, **kwargs)

def netcat(*args, **kwargs):
    """Execute netcat with intelligent argument detection."""
    return get_hats_instance().netcat(*args, **kwargs)

def socat(*args, **kwargs):
    """Execute socat with intelligent argument detection."""
    return get_hats_instance().socat(*args, **kwargs)

def tcpdump(*args, **kwargs):
    """Execute tcpdump with intelligent argument detection."""
    return get_hats_instance().tcpdump(*args, **kwargs)

def wireshark(*args, **kwargs):
    """Execute tshark (wireshark CLI) with intelligent argument detection."""
    return get_hats_instance().wireshark(*args, **kwargs)

def linpeas(*args, **kwargs):
    """Execute linpeas with intelligent argument detection."""
    return get_hats_instance().linpeas(*args, **kwargs)

def winpeas(*args, **kwargs):
    """Execute winpeas with intelligent argument detection."""
    return get_hats_instance().winpeas(*args, **kwargs)

def msfvenom(*args, **kwargs):
    """Execute msfvenom with intelligent argument detection."""
    return get_hats_instance().msfvenom(*args, **kwargs)

def binwalk(*args, **kwargs):
    """Execute binwalk with intelligent argument detection."""
    return get_hats_instance().binwalk(*args, **kwargs)

def foremost(*args, **kwargs):
    """Execute foremost with intelligent argument detection."""
    return get_hats_instance().foremost(*args, **kwargs)

def volatility(*args, **kwargs):
    """Execute volatility with intelligent argument detection."""
    return get_hats_instance().volatility(*args, **kwargs)

def dnsrecon(*args, **kwargs):
    """Execute dnsrecon with intelligent argument detection."""
    return get_hats_instance().dnsrecon(*args, **kwargs)

def dnsenum(*args, **kwargs):
    """Execute dnsenum with intelligent argument detection."""
    return get_hats_instance().dnsenum(*args, **kwargs)

def fierce(*args, **kwargs):
    """Execute fierce with intelligent argument detection."""
    return get_hats_instance().fierce(*args, **kwargs)

def steghide(*args, **kwargs):
    """Execute steghide with intelligent argument detection."""
    return get_hats_instance().steghide(*args, **kwargs)

# ============ SYSTEM COMMANDS ============
def strings(*args, **kwargs):
    """Execute strings command with intelligent argument detection."""
    return get_hats_instance().execute_tool('strings', *args, **kwargs)

def file(*args, **kwargs):
    """Execute file command with intelligent argument detection.""" 
    return get_hats_instance().execute_tool('file', *args, **kwargs)

def hexdump(*args, **kwargs):
    """Execute hexdump command with intelligent argument detection."""
    return get_hats_instance().execute_tool('hexdump', *args, **kwargs)

def wireshark_cli(*args, **kwargs):
    """Execute tshark (wireshark CLI) with intelligent argument detection."""
    return get_hats_instance().execute_tool('tshark', *args, **kwargs)

def netstat(*args, **kwargs):
    """Execute netstat command with intelligent argument detection."""
    return get_hats_instance().execute_tool('netstat', *args, **kwargs)

def ss(*args, **kwargs):
    """Execute ss command with intelligent argument detection."""
    return get_hats_instance().execute_tool('ss', *args, **kwargs)

def lsof(*args, **kwargs):
    """Execute lsof command with intelligent argument detection."""
    return get_hats_instance().execute_tool('lsof', *args, **kwargs)

def ps(*args, **kwargs):
    """Execute ps command with intelligent argument detection."""
    return get_hats_instance().execute_tool('ps', *args, **kwargs)

def dirsearch(*args, **kwargs):
    """Execute dirsearch with intelligent argument detection."""
    return get_hats_instance().execute_tool('dirsearch', *args, **kwargs)

def aircrack_ng(*args, **kwargs):
    """Execute aircrack-ng with intelligent argument detection."""
    return get_hats_instance().execute_tool('aircrack-ng', *args, **kwargs)

def hashid(*args, **kwargs):
    """Execute hashid with intelligent argument detection."""
    return get_hats_instance().execute_tool('hashid', *args, **kwargs)

def hash_identifier(*args, **kwargs):
    """Execute hash-identifier with intelligent argument detection."""
    return get_hats_instance().execute_tool('hash-identifier', *args, **kwargs)

def enum4linux(*args, **kwargs):
    """Execute enum4linux with intelligent argument detection."""
    return get_hats_instance().execute_tool('enum4linux', *args, **kwargs)

def smbmap(*args, **kwargs):
    """Execute smbmap with intelligent argument detection."""
    return get_hats_instance().execute_tool('smbmap', *args, **kwargs)

def searchsploit(*args, **kwargs):
    """Execute searchsploit with intelligent argument detection."""
    return get_hats_instance().execute_tool('searchsploit', *args, **kwargs)

def smbclient(*args, **kwargs):
    """Execute smbclient with intelligent argument detection."""
    return get_hats_instance().execute_tool('smbclient', *args, **kwargs)

def rpcclient(*args, **kwargs):
    """Execute rpcclient with intelligent argument detection."""
    return get_hats_instance().execute_tool('rpcclient', *args, **kwargs)

def showmount(*args, **kwargs):
    """Execute showmount with intelligent argument detection."""
    return get_hats_instance().execute_tool('showmount', *args, **kwargs)

# Alias for msfvenom (since metasploit console is interactive)
msploit = msfvenom

def report(*args, **kwargs):
    """Generate report from multiple tool results."""
    return get_hats_instance().report(*args, **kwargs)

# Category interfaces
recon = property(lambda self: get_hats_instance().recon)
initaccess = property(lambda self: get_hats_instance().initaccess)
execution = property(lambda self: get_hats_instance().execution)
escalation = property(lambda self: get_hats_instance().escalation)
clear_tracks = property(lambda self: get_hats_instance().clear_tracks)

# WiFi and Forensics modules (placeholders for future implementation)
class WiFiTools:
    """WiFi-specific tools (placeholder)."""
    def __init__(self):
        self.hats = get_hats_instance()
    
    def aircrack(self, *args, **kwargs):
        """Execute aircrack-ng."""
        return self.hats.aircrack(*args, **kwargs)
    
    def airodump(self, *args, **kwargs):
        """Execute airodump-ng."""
        return self.hats.airodump(*args, **kwargs)

class ForensicsTools:
    """Forensics-specific tools (placeholder)."""
    def __init__(self):
        self.hats = get_hats_instance()
    
    def autopsy(self, *args, **kwargs):
        """Execute autopsy."""
        return self.hats.autopsy(*args, **kwargs)
    
    def volatility(self, *args, **kwargs):
        """Execute volatility."""
        return self.hats.volatility(*args, **kwargs)

wifi = WiFiTools()
forensics = ForensicsTools()

__all__ = [
    # Core classes
    'HATSEngine', 
    'ToolManager', 
    'ConfigLoader', 
    'HATS',
    'DynamicToolInterface',
    'ReconTools',
    'ExploitTools',
    'PostExploitTools',
    'ArgumentSanitizer',
    'ToolResult',
    
    # Network Scanning
    'nmap',
    'masscan',
    'rustscan', 
    'zmap',
    
    # Web Scanning
    'gobuster',
    'dirb',
    'nikto',
    'whatweb',
    'wfuzz',
    'ffuf',
    
    # Vulnerability Scanning
    'nuclei',
    
    # Exploitation
    'sqlmap',
    'hydra',
    'medusa',
    'ncrack',
    'msfvenom',
    'msploit',
    
    # Password Tools
    'john',
    'hashcat',
    'crunch',
    'cewl',
    
    # Wireless
    'aircrack',
    'airodump',
    'reaver',
    
    # Networking
    'netcat',
    'socat',
    'tcpdump',
    'wireshark',
    
    # Post-Exploitation
    'linpeas',
    'winpeas',
    
    # Forensics
    'binwalk',
    'foremost',
    'volatility',
    
    # DNS Tools
    'dnsrecon',
    'dnsenum',
    'fierce',
    
    # Steganography
    'steghide',
    
    # Utilities
    'report',
    'recon',
    'initaccess',
    'execution', 
    'escalation',
    'clear_tracks',
    'wifi',
    'forensics'
]
