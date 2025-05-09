package oeg.tagger.main;

import edu.stanford.nlp.io.EncodingPrintWriter.out;
import edu.stanford.nlp.util.logging.RedwoodConfiguration;
//import javafx.scene.control.ProgressBar;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;
import oeg.tagger.core.time.tictag.Annotador;
import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.filefilter.FalseFileFilter;
import org.apache.commons.lang3.ObjectUtils.Null;

import java.util.logging.Level;
import java.util.logging.Logger;
import oeg.tagger.core.time.tictag.AnnotadorLegal;
import oeg.tagger.core.time.tictag.AnnotadorStandard;
import org.apache.maven.model.Model;
import org.apache.maven.model.io.xpp3.MavenXpp3Reader;

import java.io.*;
import java.lang.reflect.Array;
import java.util.Scanner;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;

/**
 * Main class of the jar.
 *
 * @author vroddon
 * @author mnavas
 */
public class Main {

    static final Logger logger = Logger.getLogger(Main.class.getName());
    static boolean logs = false;
    static String lang = "es";
    static String domain = "standard";
    static String date = "";
    static String format = "timeml";
    static String outpfilename = null;

    public static void main(String[] args) throws IOException {

        // We do this to avoid the Ixa-Pipes debugging messages...
        PrintStream systemerr = System.err;
        init(args);
        AnnotadorStandard annotador = new AnnotadorStandard("es");
        String anchorDate = args[0];
        String type = args[1];
        String input = args[2];
        String val = args[3];
        String freq = "";
        String text = "";
        int ini = 0;
        String res = annotador.anotarCIR(input, anchorDate, type, val, freq, ini, text);
        System.out.println(res);

        /*
         if (args.length != 0) {
             String res = parsear(args);
             
             if (!res.isEmpty()) {
                 //IMPRIME RESULTADOS (es un objeto vacío no sé porqué se pasa así. Pero da igual, el texto anotado está en parsear)
                 //System.out.println(res);
                 System.out.println();
                }
            }
        */
           
                         
        System.setErr(systemerr);
    }


    public static void resolver_cir(String csvFilePath, String language, String dataset){
        try (BufferedReader br = new BufferedReader(new FileReader(csvFilePath))) {
            String line;
            String path_dest = "/" + dataset.toLowerCase() + "_" + language + "_normalized/"; //Create if not exists
            
            List<String> etiqueta_final = new ArrayList<String>();
            String file = "";
            String cabecera = "<?xml version=\"1.0\" ?>\n<TimeML xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"http://timeml.org/timeMLdocs/TimeML_1.2.1.xsd\">\n\n<DOCID>";
            Boolean first_expresion = true;
            Integer counter_expresion = 1;
            AnnotadorStandard annotador = new AnnotadorStandard("es");
            while ((line = br.readLine()) != null) {
                // Split the CSV line using a comma as the delimiter
                String[] fields = line.split(",");
                String value = "";
                if (!fields[0].equals("File")){
                    if(!file.equals(fields[0])){
                        if(!file.isEmpty()){
                            String file_path = file.replace("xml", "tml");
                            file_path = file_path.replace("txt", "tml");
                            try (BufferedWriter writer = new BufferedWriter(new FileWriter(path_dest+file_path))) {
                                cabecera = cabecera + file + "</DOCID>\n\n<DCT>KUALA LUMPUR, <TIMEX3 tid=\"t0\" type=\"TIME\" value=\"1997-04-01\" temporalFunction=\"false\" functionInDocument=\"CREATION_TIME\">April 1 , 1997</TIMEX3> (AFP)</DCT>\n\n\n<TEXT>\n\n";
                                //System.out.println(String.join(" ", etiqueta_final));
                                String final_text = cabecera + String.join(" ", etiqueta_final) + "\n\n\n</TEXT>\n\n\n</TimeML>";
                                writer.write(final_text);
                                etiqueta_final.clear();
                                cabecera = "<?xml version=\"1.0\" ?>\n<TimeML xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"http://timeml.org/timeMLdocs/TimeML_1.2.1.xsd\">\n\n<DOCID>";
                                first_expresion = true;
                                counter_expresion = 1;
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                        }
                        file = fields[0];
                    }
                    //Uncoment to print current row
                    //System.out.println(fields[0]);
                    //System.out.println(fields[1]);
                    //System.out.println();
                    String type_ = fields[2];
                    String expresion = fields[3].trim();
                    String dct = fields[5];
                    if(fields.length > 7){
                        for (int i = 6; i < fields.length; i++){
                            if(i == fields.length-1){
                                value = value + fields[i].trim();
                            }
                            else{
                                value = value + fields[i].trim() + ",";
                            }
                        }
                    }
                    else{
                        value = fields[6];
                    }
                    if(value.equals("Nulo")){
                        if(type_.equals("DATE")){
                            value = "XXXX-XX-XX";
                        }
                        else if(type_.equals("TIME")){
                            value = "XXXX-XX-XXTXX";
                        }
                        else if(type_.equals("DURATION") || type_.equals("SET")){
                            value = "PXD";
                        }
                        //<TIMEX3 type="DURATION" value="P20D" tid="t8">los 20 días</TIMEX3>
                        String res = "<TIMEX3 type=\"" + type_ + "\" value=\"" + value + "\" tid=\"t" + counter_expresion + "\">" + expresion + "</TIMEX3>";
                        counter_expresion+=1;
                        etiqueta_final.add(res);
                    }
                    else{
                        value = value.replace("\"", "");
                        //System.out.println(value);
                        String res = annotador.anotarCIR(expresion, dct, type_, value, "", 0, expresion);
                        if(res == null){ //Hay algunos valores que dan error en annotador porque están mal formados. Para tratarlo devuelvo null de annotarCIR. En esos casos pongo el valor por defecto
                            if(type_.equals("DATE")){
                                value = "XXXX-XX-XX";
                            }
                            else if(type_.equals("TIME")){
                                value = "XXXX-XX-XXTXX";
                            }
                            else if(type_.equals("DURATION") || type_.equals("SET")){
                                value = "PXD";
                            }
                            res = "<TIMEX3 type=\"" + type_ + "\" value=\"" + value + "\" tid=\"t" + counter_expresion + "\">" + expresion + "</TIMEX3>";
                            counter_expresion+=1;
                            etiqueta_final.add(res);
                            //System.out.println(res);
                        }
                        else{
                            res = res.replace("tid=\"t0\"", "tid=\"t"+counter_expresion.toString()+"\"");
                            counter_expresion+=1;
                            etiqueta_final.add(res);
                        }
                    }
                }
            }
            String file_path = file.replace("tml", "tml");
            file_path = file.replace("xml", "tml");
            file_path = file_path.replace("txt", "tml");
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(path_dest+file_path))) {
                cabecera = cabecera + file + "</DOCID>\n\n<DCT>KUALA LUMPUR, <TIMEX3 tid=\"t0\" type=\"TIME\" value=\"1997-04-01\" temporalFunction=\"false\" functionInDocument=\"CREATION_TIME\">April 1 , 1997</TIMEX3> (AFP)</DCT>\n\n\n<TEXT>\n\n";
                //System.out.println(String.join(" ", etiqueta_final));
                String final_text = cabecera + String.join(" ", etiqueta_final) + "\n\n\n</TEXT>\n\n\n</TimeML>";
                writer.write(final_text);
                etiqueta_final.clear();
                cabecera = "<?xml version=\"1.0\" ?>\n<TimeML xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"http://timeml.org/timeMLdocs/TimeML_1.2.1.xsd\">\n\n<DOCID>";
                first_expresion = true;
                counter_expresion = 1;
            } catch (IOException e) {
                e.printStackTrace();
                System.out.println(e);
            }
        } catch (IOException e) {
            e.printStackTrace();
            System.out.println(e);
        }

    }

    public static List<List<String>> leerCSV(String path) throws IOException{
        int a = 0;
        List<String> ids = new ArrayList<String>();
        List<String> values = new ArrayList<String>();

        Scanner sc = new Scanner(new File(path));  
        sc.useDelimiter(";");   //sets the delimiter pattern  
        while (sc.hasNext())  //returns a boolean value  
        {  
            String[] act = sc.nextLine().split(";");
                         
            if (a == 0){
                a++;
            }
            else{
                ids.add(act[0]);
                values.add(act[3]);   
            }
            
        }   
        sc.close();

        List<List<String>> ids_values = new ArrayList<List<String>>();
        ids_values.add(ids);
        ids_values.add(values);
        return ids_values;
    }   


    public static void anotarDesdeFicheros(String pathText, String pathDCT, String pathDest) throws IOException{
        // Create a File object for the folder
        File folder = new File(pathText);
        File[] files = folder.listFiles();
        int actual_file_count = 0;
        long startTime = System.currentTimeMillis();
        System.out.println("\n\n######### START #########\n\n");
        System.out.print("REMAINING: " + actual_file_count + "/" + files.length);
        List<List<String>> dcts = leerCSV(pathDCT);
        Charset encoding = StandardCharsets.UTF_8; 
        String dct = "";
        for (File file : files) {
            String [] path_string_split = file.toString().split("/");
            String file_string = path_string_split[path_string_split.length-1];
            String string = "";
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(file), encoding))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    // Process each line of text
                    string += line;
                }
                
                if (dcts.contains(file.getName())){
                    int index = dcts.get(0).indexOf(file.getName());
                    dct = dcts.get(1).get(index);
                }
                else {
                    dct = "2000-01-01";
                }
                String annotated_string = parseText(string, dct);
                String pathDestFile = pathDest + file_string;

                try (BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(pathDestFile), encoding))) {
                    writer.write(annotated_string);
                }catch (IOException e) {
                    e.printStackTrace();
                }
                actual_file_count++;
                System.out.print("\rREMAINING: " + actual_file_count + "/" + files.length + '\r');
                    
            } catch (IOException e) {
                e.printStackTrace();
            }
        } 
        System.out.println("\n\n######### END #########\n\n");
        long endTime = System.currentTimeMillis();

        // Calculate the execution time
        long executionTime = (endTime - startTime)/1000;

        System.out.println("Execution time in seconds: " + executionTime + " s");
        

    }

    public static void init(String[] args) {
        logs = Arrays.asList(args).contains("-logs");
        initLogger(logs);
        
        
        //Welcome message
        try {
            MavenXpp3Reader reader = new MavenXpp3Reader();
            Model model = reader.read(new FileReader("pom.xml"));
            String welcome = model.getArtifactId() + " " + model.getVersion() + "\n-----------------------------------------------------\n";
            logger.info(welcome);
        } catch (Exception e) {
        }

    }
    public static String parsear(String[] args) {
        ///Response
        System.out.println(args);
        StringBuilder res = new StringBuilder();
        CommandLineParser parser = null;
        CommandLine cmd = null;
        try {
            Options options = new Options();
            options.addOption("nologs", false, "OPTION to disables logs");
            options.addOption("logs", false, "OPTION to enable logs");
            options.addOption("lang", true, "OPTION to change language [ES, EN] (Spanish by default)");
            options.addOption("domain", true, "OPTION to change domain [standard, legal] (Standard by default)");
            options.addOption("date", true, "OPTION to add an anchor date in the format yyyy-mm-dd (today by default)");
            options.addOption("text", true, "COMMAND to parse a text");
            options.addOption("f", true, "COMMAND to parse a file");
            options.addOption("outf", true, "COMMAND to save the output to a file"); 
            options.addOption("format", true, "COMMAND to choose the output format [timeml,json,nif] (TimeML by default)"); 
            options.addOption("help", false, "COMMAND to show help (Help)");
            parser = new BasicParser();
            cmd = parser.parse(options, args);
            String outp = "";

            if (cmd.hasOption("help") || args.length == 0) {
                new HelpFormatter().printHelp(Main.class.getCanonicalName(), options);
            }
            if (cmd.hasOption("lang")) {
                lang = cmd.getOptionValue("lang");
            }
            if (cmd.hasOption("domain")) {
                domain = cmd.getOptionValue("domain");
            }
//            if (!cmd.hasOption("logs")) {
//                initLoggerDisabled();
//            }
            if (cmd.hasOption("date")) {
                date = cmd.getOptionValue("date");
            }
            if (cmd.hasOption("format")) {
                format = cmd.getOptionValue("format");
            }
            if (cmd.hasOption("f")) {
                String filename = cmd.getOptionValue("f");
                logger.info("Trying to parse the file " + filename);
                outp = parse(filename);
            }
            if (cmd.hasOption("text")) {
                String text = cmd.getOptionValue("text");
                logger.info("Trying to process the text " + text);
                outp = parseText(text, "");
            }
            if(cmd.hasOption("outf")){
                outpfilename = cmd.getOptionValue("outf");
                if(!writeFile(outp, outpfilename)){
                    logger.warning("Error while writing."); // ERROR
                } else{
                    logger.info("Output correctly written to " + outpfilename);
                }
            }

            if(outp != null){                
                if(logs){
                    System.out.println("\n----------------\n");
                }
                System.out.println(outp);
                if(logs){
                    System.out.println("\n----------------\n");
                }
            }

        } catch (Exception e) {
            System.out.println(e.toString());
            System.out.println("ERROR");
        }
        return res.toString();
    }

    public static String parse(String filename) {   
        String res = "";
        try {
            File f = new File(filename);
            logger.info("parsing the folder " + filename); // DEBUG
            String input = FileUtils.readFileToString(f, "UTF-8");
            res = parseText(input, "");
                
        } catch (Exception e) {
            logger.warning("error opening file"); // ERROR
            return "";
        }
        logger.info("Parsing correct\n\n");
        return res;
    }
    
    public static String parseText(String txt, String DCT) {
        String res = "";
        Date dct = null;
        try{
            if (!date.matches("\\d\\d\\d\\d-(1[012]|0\\d)-(3[01]|[012]\\d)")) // Is it valid?
        {
            logger.info("No correct date provided, ");
            dct = Calendar.getInstance().getTime();
            DateFormat df = new SimpleDateFormat("yyyy-MM-dd");
            date = df.format(dct);
            //date = "1997-04-01";
            date = DCT;
        }
        
        Annotador annotador;
        
        if(domain.equalsIgnoreCase("standard")){
            if(lang.equalsIgnoreCase("ES")){
                   // We innitialize the tagger in Spanish        
                   annotador = new AnnotadorStandard("es");
            }
            else if(lang.equalsIgnoreCase("EN")){
                annotador = new AnnotadorStandard("en");
            }
            else{
                logger.warning("error in language; for now, just available ES and EN"); // ERROR
                return res;
            }
        } else if(domain.equalsIgnoreCase("legal")){
            if(lang.equalsIgnoreCase("ES")){
                   // We innitialize the tagger in Spanish        
                   annotador = new AnnotadorLegal("es");
            }
            else if(lang.equalsIgnoreCase("EN")){
                annotador = new AnnotadorLegal("en");
            }
            else{
                logger.warning("error in language; for now, just available ES and EN"); // ERROR
                return res;
            }
        } else{
            logger.warning("error in domain; for now, just available standard and legal"); // ERROR
                return res;
        }
        
        if(format.equalsIgnoreCase("timeml")){
            res = annotador.annotate(txt, date);
        } else if(format.equalsIgnoreCase("nif")){
            res = annotador.annotateNIF(txt, date, "ref", lang);
        } else if(format.equalsIgnoreCase("json")){
            res = annotador.annotateJSON(txt, date);
        } else{
            logger.warning("Incorrect format; TimeML will be used."); // ERROR
            res = annotador.annotate(txt, date);
        }
        
        } catch (Exception e) {
            logger.warning("error processing text:\n" + res); // ERROR
            return "";
        }
       logger.info("Text processing correct:\n" + res);

        return res;
    }

    public static void initLogger(boolean logs) {
        if (logs) {
            initLoggerDebug();
        } else {
            initLoggerDisabled();
        }

    }

    /**
     * Shuts up all the loggers. 
     * Also the logs from third parties.
     */
    private static void initLoggerDisabled() {
        Logger.getLogger("").setLevel(Level.FINEST);
//
//        List<Logger> loggers = Collections.<Logger>list(LogManager.getCurrentLoggers());
//        loggers.add(LogManager.getRootLogger());
//        for (Logger log : loggers) {
//            log.setLevel(Level.OFF);
//        }
//        Logger.getRootLogger().setLevel(Level.OFF);
        
        // We do this to void IxaPipes messages...
        PrintStream falseerr = new PrintStream(new OutputStream(){
            public void write(int b) {
            }
        });
        System.setErr(falseerr);
        
        // We turn off CoreNLP logger
        RedwoodConfiguration.current().clear().apply();        
        
        // We turn off some inner IxaPipes loggers
//        ch.qos.logback.classic.Logger logger1 = (ch.qos.logback.classic.Logger) LoggerFactory.getLogger(SpanishReadabilityModel.class);
//        logger1.setLevel(ch.qos.logback.classic.Level.OFF);           
//        ch.qos.logback.classic.Logger logger2 = (ch.qos.logback.classic.Logger) LoggerFactory.getLogger(Hyphenator.class);
//        logger2.setLevel(ch.qos.logback.classic.Level.OFF);
//        ch.qos.logback.classic.Logger logger3 = (ch.qos.logback.classic.Logger) LoggerFactory.getLogger(BasicAnnotator.class);
//        logger3.setLevel(ch.qos.logback.classic.Level.OFF);
//        
//        logger.setLevel(Level.OFF);

//        Logger.getRootLogger().removeAllAppenders();
//Logger.getRootLogger().addAppender(new NullAppender());
    }

    /**
     * Si se desean logs, lo que se hace es: - INFO en consola - DEBUG en
     * archivo de logs logs.txt
     */
    private static void initLoggerDebug() {

//        Enumeration currentLoggers = LogManager.getCurrentLoggers();
//        List<Logger> loggers = Collections.<Logger>list(currentLoggers);
//        loggers.add(LogManager.getRootLogger());
//        for (Logger log : loggers) {
//            log.setLevel(Level.OFF);
//        }
//
//        Logger root = Logger.getRootLogger();
//        root.setLevel((Level) Level.DEBUG);
//
//        //APPENDER DE CONSOLA (INFO)%d{ABSOLUTE} 
//        PatternLayout layout = new PatternLayout("%d{HH:mm:ss} [%5p] %13.13C{1}:%-4L %m%n");
//        ConsoleAppender appenderconsole = new ConsoleAppender(); //create appender
//        appenderconsole.setLayout(layout);
//        appenderconsole.setThreshold(Level.INFO);
//        appenderconsole.activateOptions();
//        appenderconsole.setName("console");
//        root.addAppender(appenderconsole);
//
//        //APPENDER DE ARCHIVO (DEBUG)
//        PatternLayout layout2 = new PatternLayout("%d{ISO8601} [%5p] %13.13C{1}:%-4L %m%n");
//        FileAppender appenderfile = null;
//        String filename = "./logs/logs.txt";
//        try {
//            MavenXpp3Reader reader = new MavenXpp3Reader();
//            Model model = reader.read(new FileReader("pom.xml"));
//            filename = "./logs/" + model.getArtifactId() + ".txt";
//        } catch (Exception e) {
//        }
//        try {
//            appenderfile = new FileAppender(layout2, filename, false);
//            appenderfile.setName("file");
//            appenderfile.setThreshold(Level.DEBUG);
//            appenderfile.activateOptions();
//        } catch (Exception e) {
//        }
//
//        root.addAppender(appenderfile);
//
//
//        logger = Logger.getLogger(Main.class.getName());
    }
    public static boolean writeFile(String input, String path) {
        try {
            FileOutputStream fos = new FileOutputStream(path);
            OutputStreamWriter w = new OutputStreamWriter(fos, "UTF-8");
            BufferedWriter bw = new BufferedWriter(w);
            bw.write(input);
            bw.flush();
            bw.close();
            return true;
        } catch (Exception ex) {
            java.util.logging.Logger.getLogger(Annotador.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
        }
        return false;
    }

}
