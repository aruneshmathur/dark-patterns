import javax.xml.namespace.NamespaceContext;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.*;
import org.w3c.dom.*;
import org.xml.sax.*;
import java.io.*;

import org.w3c.dom.Document;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.net.URLConnection;
import java.net.HttpURLConnection;
import java.net.URLEncoder;
import java.security.SignatureException;
import java.security.MessageDigest;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * Simple demo showing how to make a successful request to Alexa Top Sites.
 * <p/>
 * Note that you must sign up for Alexa Top Sites at
 * http://aws.amazon.com/alexatopsites before running this demo.
 */
public class TopSites {
	protected static final String ACTION_NAME = "TopSites";
	protected static final String RESPONSE_GROUP_NAME = "Country";
	protected static final String SERVICE_HOST = "ats.amazonaws.com";
	protected static final String SERVICE_ENDPOINT = "ats.us-west-1.amazonaws.com";
	private static final String SERVICE_URI = "/api";
	private static final String SERVICE_REGION = "us-west-1";
	private static final String SERVICE_NAME = "AlexaTopSites";
	protected static final String AWS_BASE_URL = "https://" + SERVICE_HOST + SERVICE_URI;

	protected static final int NUMBER_TO_RETURN = 100;
	protected static final String DATEFORMAT_AWS = "yyyyMMdd'T'HHmmss'Z'";
	protected static final String DATEFORMAT_CREDENTIAL = "yyyyMMdd";
	private static final String HASH_ALGORITHM = "HmacSHA256";

	private String accessKeyId;
	private String secretAccessKey;

	public String amzDate;
	public String dateStamp;

	public TopSites(String accessKeyId, String secretAccessKey) {
		this.accessKeyId = accessKeyId;
		this.secretAccessKey = secretAccessKey;

		Date now = new Date();
		SimpleDateFormat formatAWS = new SimpleDateFormat(DATEFORMAT_AWS);
		formatAWS.setTimeZone(TimeZone.getTimeZone("GMT"));
		this.amzDate = formatAWS.format(now);

		SimpleDateFormat formatCredential = new SimpleDateFormat(DATEFORMAT_CREDENTIAL);
		formatCredential.setTimeZone(TimeZone.getTimeZone("GMT"));
		this.dateStamp = formatCredential.format(now);
	}

	String sha256(String textToHash) throws Exception {
		MessageDigest digest = MessageDigest.getInstance("SHA-256");
		byte[] byteOfTextToHash = textToHash.getBytes("UTF-8");
		byte[] hashedByteArray = digest.digest(byteOfTextToHash);
		return bytesToHex(hashedByteArray);
	}

	static byte[] HmacSHA256(String data, byte[] key) throws Exception {
		Mac mac = Mac.getInstance(HASH_ALGORITHM);
		mac.init(new SecretKeySpec(key, HASH_ALGORITHM));
		return mac.doFinal(data.getBytes("UTF8"));
	}

	public static String bytesToHex(byte[] bytes) {
		StringBuffer result = new StringBuffer();
		for (byte byt : bytes)
			result.append(Integer.toString((byt & 0xff) + 0x100, 16).substring(1));
		return result.toString();
	}

	static byte[] getSignatureKey(String key, String dateStamp, String regionName, String serviceName)
			throws Exception {
		byte[] kSecret = ("AWS4" + key).getBytes("UTF8");
		byte[] kDate = HmacSHA256(dateStamp, kSecret);
		byte[] kRegion = HmacSHA256(regionName, kDate);
		byte[] kService = HmacSHA256(serviceName, kRegion);
		byte[] kSigning = HmacSHA256("aws4_request", kService);
		return kSigning;
	}

	/**
	 * Makes a request to the specified Url and return the results as a String
	 *
	 * @param requestUrl
	 *            url to make request to
	 * @return the XML document as a String
	 * @throws IOException
	 */
	public static String makeRequest(String requestUrl, String authorization, String amzDate) throws IOException {
		URL url = new URL(requestUrl);
		HttpURLConnection conn = (HttpURLConnection) url.openConnection();
		conn.setRequestProperty("Accept", "application/xml");
		conn.setRequestProperty("Content-Type", "application/xml");
		conn.setRequestProperty("X-Amz-Date", amzDate);
		conn.setRequestProperty("Authorization", authorization);

		InputStream in = (conn.getResponseCode() / 100 == 2 ? conn.getInputStream() : conn.getErrorStream());

		// Read the response
		StringBuffer sb = new StringBuffer();
		int c;
		int lastChar = 0;
		while ((c = in.read()) != -1) {
			if (c == '<' && (lastChar == '>'))
				sb.append('\n');
			sb.append((char) c);
			lastChar = c;
		}
		in.close();
		return sb.toString();
	}

	/**
	 * Makes a request to the Alexa Top Sites Service TopSites action
	 */
	public static void main(String[] args) throws Exception {
		if (args.length < 2) {
			System.out.println("Usage: java AlexaTopSites ACCESS_KEY_ID " + "SECRET_ACCESS_KEY TOTAL_SITES");
			System.exit(-1);
		}

		String accessKey = args[0];
		String secretKey = args[1];
		String totalSites = args[2];

    for (int i = 1; i < Integer.valueOf(totalSites); i += 100) {
      List<Site> result = queueRequests(accessKey, secretKey, String.valueOf(i));

      for (Site s: result) {
        System.out.println(s);
      }
    }
	}

  public static List<Site> queueRequests(String accessKey, String secretKey, String startNumber) throws Exception {
    TopSites topSites = new TopSites(accessKey, secretKey);

    String canonicalQuery = "Action=" + ACTION_NAME + "&Count=" + NUMBER_TO_RETURN + "&ResponseGroup="
        + RESPONSE_GROUP_NAME + "&Start=" + startNumber;
    String canonicalHeaders = "host:" + SERVICE_ENDPOINT + "\n" + "x-amz-date:" + topSites.amzDate + "\n";
    String signedHeaders = "host;x-amz-date";

    String payloadHash = topSites.sha256("");

    String canonicalRequest = "GET" + "\n" + SERVICE_URI + "\n" + canonicalQuery + "\n" + canonicalHeaders + "\n"
        + signedHeaders + "\n" + payloadHash;

    // ************* TASK 2: CREATE THE STRING TO SIGN*************
    // Match the algorithm to the hashing algorithm you use, either SHA-1 or
    // SHA-256 (recommended)
    String algorithm = "AWS4-HMAC-SHA256";
    String credentialScope = topSites.dateStamp + "/" + SERVICE_REGION + "/" + SERVICE_NAME + "/" + "aws4_request";
    String stringToSign = algorithm + '\n' + topSites.amzDate + '\n' + credentialScope + '\n'
        + topSites.sha256(canonicalRequest);

    // ************* TASK 3: CALCULATE THE SIGNATURE *************
    // Create the signing key
    byte[] signingKey = topSites.getSignatureKey(secretKey, topSites.dateStamp, SERVICE_REGION, SERVICE_NAME);

    // Sign the string_to_sign using the signing_key
    String signature = bytesToHex(HmacSHA256(stringToSign, signingKey));

    String uri = AWS_BASE_URL + "?" + canonicalQuery;

    String authorization = algorithm + " " + "Credential=" + accessKey + "/" + credentialScope + ", "
        + "SignedHeaders=" + signedHeaders + ", " + "Signature=" + signature;

    String xmlResponse = makeRequest(uri, authorization, topSites.amzDate);

    return getFormattedResponse(xmlResponse);
  }

	public static List<Site> getFormattedResponse(String xmlResponse) throws Exception {
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder builder = factory.newDocumentBuilder();
		Document doc = builder.parse(new InputSource(new StringReader(xmlResponse)));

		NodeList nList = doc.getElementsByTagName("aws:Site");

		List<Site> result = new ArrayList<Site>();

		for (int i = 0; i < nList.getLength(); i++) {
			Node node = nList.item(i);
			Site site = new Site();

			NodeList childNodes = node.getChildNodes();
			for (int j = 0; j < childNodes.getLength(); j++) {
				Node childNode = childNodes.item(j);
				if (childNode.getNodeName() == "aws:DataUrl") {
					site.setURL(childNode.getTextContent());
				} else if (childNode.getNodeName() == "aws:Global") {
					site.setGlobalRank(Integer
							.valueOf(((Element) childNode).getElementsByTagName("aws:Rank").item(0).getTextContent()));
				} else if (childNode.getNodeName() == "aws:Country") {
					site.setCountryRank(Integer
							.valueOf(((Element) childNode).getElementsByTagName("aws:Rank").item(0).getTextContent()));
					site.setReachPerMillion(Double
							.valueOf(((Element) childNode).getElementsByTagName("aws:Reach").item(0).getTextContent()));

					site.setPageViewsPerMillion(Double
							.valueOf(((Element) ((Element) childNode).getElementsByTagName("aws:PageViews").item(0))
									.getElementsByTagName("aws:PerMillion").item(0).getTextContent()));
					site.setPageViewsPerUser(Double
							.valueOf(((Element) ((Element) childNode).getElementsByTagName("aws:PageViews").item(0))
									.getElementsByTagName("aws:PerUser").item(0).getTextContent()));
				} else {
					// Do nothing
				}
			}

			result.add(site);
		}

		return result;
	}
}
